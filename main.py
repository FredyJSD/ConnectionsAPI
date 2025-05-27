from flask import Flask, jsonify, render_template, request
import random
import boto3
import uuid


app = Flask(__name__)

# CREATE DB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
prompts_table = dynamodb.Table('Prompts')
sessions_table = dynamodb.Table('Sessions')
users_table = dynamodb.Table('Users')


# CREATE TABLE
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
    # Add prompt to DynamoDB
    pass

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
