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



@app.route("/prompts", methods=["GET"])
def get_prompts():
    # Scan table and return items
    pass


@app.route("/prompts", methods=["POST"])
def add_prompt():
    data = request.json

    user_id = get_user_id_from_request()
    text = data.get("text")
    level = data.get("level")

    prompt_id = create_prompt(text, level, user_id)
    return jsonify({"prompt_id": prompt_id}), 201


@app.route("/prompts/<id>", methods=["DELETE"])
def delete_prompt(id):
    # Delete prompt by ID from DynamoDB
    pass


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
