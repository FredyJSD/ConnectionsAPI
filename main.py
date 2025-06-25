from flask import Flask, jsonify, render_template, request, redirect, session, url_for, abort
from authlib.integrations.flask_client import OAuth
import os
import random
import boto3
from boto3.dynamodb.conditions import Key
import uuid
from jose import jwt
from functools import wraps
from dotenv import load_dotenv
import requests
from datetime import datetime, timezone


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "random-key")
oauth = OAuth(app)


oauth.register(
  name='oidc',
  authority='https://cognito-idp.us-east-1.amazonaws.com/us-east-1_SHWrmEyPe',
  client_id=os.getenv('CLIENT_ID'),
  client_secret=os.getenv('COGNITO_CLIENT_SECRET'),
  server_metadata_url='https://cognito-idp.us-east-1.amazonaws.com/us-east-1_SHWrmEyPe/.well-known/openid-configuration',
  client_kwargs={'scope': 'phone openid email'}
)

# CREATE DB
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('COGNITO_REGION'))
prompts_table = dynamodb.Table('Prompts')
sessions_table = dynamodb.Table('Sessions')
users_table = dynamodb.Table('Users')

# Cognito SDK client
cognito_client = boto3.client('cognito-idp', region_name=os.getenv('COGNITO_REGION'))

# Load public keys to verify tokens
JWKS_URL = f"https://cognito-idp.{os.getenv('COGNITO_REGION')}.amazonaws.com/{os.getenv('USER_POOL_ID')}/.well-known/jwks.json"
JWKS = requests.get(JWKS_URL).json()["keys"]


# --------------------
# Helper Functions for Verification
# --------------------


# VERIFY TOKEN
def verify_token(token):
    headers = jwt.get_unverified_header(token)

    key = None
    for k in JWKS:
        if k["kid"] == headers["kid"]:
            key = k
            break

    if key is None:
        raise ValueError("No matching key found for the given 'kid'")

    claims = jwt.decode(
        token, 
        key, 
        algorithms=["RS256"], 
        audience=os.getenv("CLIENT_ID"), 
        issuer=f"https://cognito-idp.{os.getenv('COGNITO_REGION')}.amazonaws.com/{os.getenv('USER_POOL_ID')}"
    )
    return claims


# GET USER ID FROM TOKEN
def get_user_id_from_request():
    if 'user' in session:
        return session["user"].get("sub")
    
    auth_header = request.headers.get("Authorization", "") #Get authorization from header (Bearer token)
    token = auth_header.replace("Bearer ", "") #Obtains just the raw token itself

    try:
        claims = verify_token(token)
        return claims["sub"]  # user_id from Cognito
    except Exception:
        abort(401, description="Invalid or missing token")

# Register New User 
def register_user(username, email, password):
    try:
        cognito_client.sign_up(
            ClientId=os.getenv('CLIENT_ID'),
            Username=username,
            Password=password,
            UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            },
            ],
        )
        return {"message": "User registered. Please confirm via email."}
    except Exception as e:
        return {"error": f"Signup failed: {str(e)}"}


# Login User and Obtain JWT Token
def login_user(email, password):
    try:
        response = cognito_client.initiate_auth(
            ClientId = os.getenv('CLIENT_ID'),
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters = {
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        return {
            "access_token": response["AuthenticationResult"]["AccessToken"],
            "id_token": response["AuthenticationResult"]["IdToken"]
        }
    except Exception as e:
        return {"error": f"Login failed: {str(e)}"}
    


# --------------------
# Helper Functions for Endpoints
# --------------------


# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return f(*args, **kwargs)

        authorization_header = request.header.get("Authorization", "")
        token = authorization_header.replace("Bearer ", "")
        try:
            claims = verify_token(token)
            # Optionally cache in request context or session
            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Authentication required"}), 401

    return decorated_function


# GET PROMPTS
def get_all_admin_prompts():
    response = prompts_table.query(
        IndexName="UserIndex",
        KeyConditionExpression=Key("user_id").eq("ADMIN")
    )
    return response["Items"]


def get_all_user_prompts(user_id):
    response = prompts_table.query(
        IndexName="UserIndex",
        KeyConditionExpression=Key("user_id").eq(user_id)
    )
    return response["Items"]


def get_specific_prompt(prompt_id):
    response = prompts_table.get_item(
        Key={"prompt_id": prompt_id}
    )

    return response["Item"] #Will return None if not found


# CREATE PROMPT
def create_prompt(prompt_text, level, user_id):
    prompt_id = str(uuid.uuid4())
    prompts_table.put_item(Item={
        'prompt_id': prompt_id, 
        'text': prompt_text,
        'level': level,
        'user_id': user_id,       
        'public': True
    })
    return prompt_id


# Delete Prompts
def delete_prompt_by_id(prompt_id):
    prompts_table.delete_item(Key={'prompt_id': prompt_id})


# Create Session
def create_session(user_id, session_id, prompts):
    sessions_table.put_item(Item={
        'session_id': session_id,
        'user_id': user_id,
        'prompts': prompts, 
        'created_at': datetime.utcnow().isoformat() + "Z"
    })
    return jsonify({'Created Session': session_id})


# Get 10 Prompts for Session
def session_prompts(user_id, level=None):
    admin_prompts = get_all_admin_prompts()
    user_prompts = get_all_user_prompts(user_id)
    all_prompts = admin_prompts + user_prompts

    if level:
        all_prompts = [p for p in all_prompts if level.lower() == p.get("level").lower()]

    random.shuffle(all_prompts)
    selected_prompts = all_prompts[:10]
    
    response = []
    for prompt in selected_prompts:
        response.append({
            'prompt_id': prompt["prompt_id"],
            'text': prompt['prompt_text'],
            'level': prompt['level'],
            'response': None
        })

    return response

# Get Specific Session
def get_session(session_id):
    response = sessions_table.get_item(
        Key={"session_id": session_id}
    )

    return response["Item"] #Will return None if not found


# Delete Session
def delete_session_record(session_id):
    sessions_table.delete_item(Key={'session_id': session_id})


# Get Session Prompts
def get_session_prompts(session_id):
    response = sessions_table.get_item(
        Key={'session_id': session_id}
    )

    item = response["Item"]

    if not item:
        return jsonify({'error': 'Session not found'}), 404
    
    prompts = item["prompts"]
    if prompts is None:
        return jsonify({'error': 'Prompts not found for this session'}), 404

    return jsonify({'prompts': prompts}), 200


# Response Helper Function
def prompt_response(session_id, data):
    if "prompt_id" not in data or "response" not in data:
        return jsonify({"error": "Missing prompt_id or response"}), 400

    response = sessions_table.get_item(
        Key={'session_id': session_id}
    )
    item = response["Item"]

    if not item:
        return jsonify({'error': 'Session not found'}), 404
    
    prompts = item["prompts"]

    if prompts is None:
        return jsonify({'error': 'Prompts not found for this session'}), 404

    for prompt in prompts:
        if prompt["prompt_id"] == data["prompt_id"]:
            if prompt["response"] == None:
                prompt["response"] = data["response"]
                sessions_table.put_item(Item=item)
                return jsonify({"status": "success", "message": "Response recorded"}), 201
            else:
                return jsonify({"Response Already Exists": prompt['response']}), 403
    
    return jsonify({"error": "Prompt ID not found in session"}), 404


# --------------------
# Auth Endpoints
# --------------------

@app.route('/register', methods=["POST"])
def register():
    data = request.json
    result = register_user(data["username"], data["email"], data["password"])
    return jsonify(result)


@app.route('/login', methods=["POST"])
def login():
    data = request.json
    result = login_user(data["email"], data["password"])
    return jsonify(result)


# @app.route('/authorize')
# def authorize():
#     token = oauth.oidc.authorize_access_token()
#     user = token['userinfo']
#     session['user'] = user
#     return redirect(url_for('index'))


@app.route("/me", methods=["GET"])
@login_required
def me():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        claims = verify_token(token)
        return jsonify({
            "user_id": claims["sub"],
            "email": claims.get("email")
        }), 200
    except Exception:
        return jsonify({"error": "Invalid token"}), 401

# --------------------
# Prompts Endpoints
# --------------------


# Obtains either all prompts or filters prompts to obtain all prompts of the same level
@app.route("/prompts", methods=["GET"])
@login_required
def get_all_prompts():
    user_id = get_user_id_from_request()

    admin_prompts = get_all_admin_prompts()
    user_prompts = get_all_user_prompts(user_id)
    all_prompts = admin_prompts + user_prompts

    if request.args.get("level"):
        filtered_prompts = []
        for prompt in all_prompts:
            if prompt["level"].lower() == request.args.get("level").lower():
                filtered_prompts.append(prompt)
        return jsonify(filtered_prompts), 200
    else:
        return jsonify(all_prompts), 200


# Obtains a specific prompt from a specific level
@app.route("/prompts/random", methods=["GET"])
@login_required
def get_random_prompt():
    level = request.args.get("level")
    #First check if level is provided, otherwise provide error
    if not level:
        return jsonify({"error": "Missing level query parameter"}), 400

    user_id = get_user_id_from_request()

    admin_prompts = get_all_admin_prompts()
    user_prompts = get_all_user_prompts(user_id)
    all_prompts = admin_prompts + user_prompts

    filtered_prompts = []

    for prompt in all_prompts:
            if prompt["level"].lower() == level.lower():
                filtered_prompts.append(prompt)

    prompt = random.choice(filtered_prompts)

    return jsonify(prompt), 200


# Add a prompt
@app.route("/prompts", methods=["POST"])
@login_required
def add_prompt():
    data = request.json

    user_id = get_user_id_from_request()
    text = data.get("text")
    level = data.get("level")

    prompt_id = create_prompt(text, level, user_id)
    return jsonify({"prompt_id": prompt_id}), 201


# Delete prompt by ID from DynamoDB
@app.route("/prompts/<id>", methods=["DELETE"])
@login_required
def delete_prompt(id):
    prompt_to_delete = get_specific_prompt(id)

    if not prompt_to_delete:
        return jsonify({"error": "Prompt doesn't exist"}), 404
    
    user_id = get_user_id_from_request()

    if user_id != prompt_to_delete["user_id"]:
        return jsonify({"error": "User doesn't have permission"}), 403
    
    delete_prompt_by_id(id)
    return jsonify({"message": f"Success: Prompt {id} deleted"}), 200


# --------------------
# Session Endpoints
# --------------------


@app.route("/sessions/new/<session_id>", methods=["POST"])
@login_required
def sessions(session_id):
    level = request.args.get("level")
    user_id = get_user_id_from_request()
    prompts = session_prompts(user_id, level)
    create_session(user_id, session_id, prompts)
    return jsonify({"session_id": session_id}), 201



@app.route("/sessions/<session_id>", methods=["GET"])
@login_required
def get_session(session_id):
    return get_session_prompts(session_id)


@app.route("/sessions/<session_id>/respond", methods=["POST"])
@login_required
def respond(session_id):
    data = request.json
    return prompt_response(session_id, data)


@app.route("/sessions/<session_id>", methods=["DELETE"])
@login_required
def delete_session(session_id):
    session_to_delete = get_session(session_id)

    if not session_to_delete:
        return jsonify({"error": "Prompt doesn't exist"}), 404
    
    user_id = get_user_id_from_request()

    if user_id != session_to_delete["user_id"]:
        return jsonify({"error": "User doesn't have permission"}), 403
    
    delete_session_record(session_id)
    return jsonify({"message": f"Success: Session {session_id} deleted"}), 200


@app.route('/logout')
def logout():
    session.pop('user', None)
    return jsonify("User Logged Out")


if __name__ == '__main__':
    app.run(debug=True)
