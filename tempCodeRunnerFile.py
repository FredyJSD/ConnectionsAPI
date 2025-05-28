from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from authlib.integrations.flask_client import OAuth
import os
import random
import boto3
from boto3.dynamodb.conditions import Key
import uuid
from jose import jwt
from functools import wraps
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "random-key")
oauth = OAuth(app)
load_dotenv()


oauth.register(
  name='oidc',
  authority='https://cognito-idp.us-east-1.amazonaws.com/us-east-1_SHWrmEyPe',
  client_id=os.getenv('CLIENT_ID'),
  client_secret=os.getenv('COGNITO_CLIENT_SECRET'),
  server_metadata_url='https://cognito-idp.us-east-1.amazonaws.com/us-east-1_SHWrmEyPe/.well-known/openid-configuration',
  client_kwargs={'scope': 'phone openid email'}
)

# CREATE DB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
prompts_table = dynamodb.Table('Prompts')
sessions_table = dynamodb.Table('Sessions')
users_table = dynamodb.Table('Users')


#GET USER ID FROM TOKEN (UNVERIFIED)
def get_user_id_from_request():
    if 'user' in session:
        return session["user"].get("sub")
    
    auth_header = request.headers.get("Authorization", "") #Get authorization from header (Bearer token)
    token = auth_header.replace("Bearer ", "") #Obtains just the raw token itself
    try:
        claims = jwt.get_unverified_claims(token)
        return claims["sub"]  # user_id from Cognito
    except Exception:
        os.abort(401, description="Invalid or missing token")


# --------------------
# Helper Functions
# --------------------


# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.accept_mimetypes.best == 'application/json': #For API Calls return JSON
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
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


@app.route('/')
def index():
    user = session.get('user')
    if user:
        return  f'Hello, {user["email"]}. <a href="/logout">Logout</a>'
    else:
        return f'Welcome! Please <a href="/login">Login</a>.'

# --------------------
# Auth Endpoints
# --------------------


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.oidc.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    token = oauth.oidc.authorize_access_token()
    user = token['userinfo']
    session['user'] = user
    return redirect(url_for('index'))


@app.route("/me", methods=["GET"])
@login_required
def me():
    user = session.get("user")
    return jsonify({
        "user_id": user.get("sub"),
        "email": user.get("email")
    }), 200


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
# Session Endpoints (Stubbed)
# --------------------


@app.route("/sessions", methods=["POST"])
@app.route("/sessions/<id>", methods=["GET"])
@app.route("/sessions/<id>/respond", methods=["POST"])
def sessions():
    pass


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
