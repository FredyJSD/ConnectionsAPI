from flask import Flask, jsonify, render_template, request
import random
import boto3
from boto3.dynamodb.conditions import Key
import uuid
from jose import jwt



app = Flask(__name__)

# CREATE DB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
prompts_table = dynamodb.Table('Prompts')
sessions_table = dynamodb.Table('Sessions')
users_table = dynamodb.Table('Users')


#GET USER ID FROM TOKEN (UNVERIFIED)
def get_user_id_from_request():
    auth_header = request.headers.get("Authorization", "") #Get authorization from header (Bearer token)
    token = auth_header.replace("Bearer ", "") #Obtains just the raw token itself

    claims = jwt.get_unverified_claims(token)
    return claims["sub"]  # user_id from Cognito


# --------------------
# Helper Functions
# --------------------


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


@app.route("/")
def home():
    return render_template("index.html")


# --------------------
# Auth Endpoints
# --------------------


@app.route("/register", methods=["POST"])
def register():
    pass


@app.route("/login", methods=["POST"])
def login():
    pass


@app.route("/me", methods=["GET"])
def me():
    pass


# --------------------
# Prompts Endpoints
# --------------------


# Obtains either all prompts or filters prompts to obtain all prompts of the same level
@app.route("/prompts", methods=["GET"])
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
        return jsonify(all_prompts["text"]), 200


# Obtains a specific prompt from a specific level
@app.route("/prompts/random", methods=["GET"])
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
def add_prompt():
    data = request.json

    user_id = get_user_id_from_request()
    text = data.get("text")
    level = data.get("level")

    prompt_id = create_prompt(text, level, user_id)
    return jsonify({"prompt_id": prompt_id}), 201


# Delete prompt by ID from DynamoDB
@app.route("/prompts/<id>", methods=["DELETE"])
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


if __name__ == '__main__':
    app.run(debug=True)
