from flask import Blueprint, request, jsonify
from boto3.dynamodb.conditions import Key
import uuid
import random
from utils import get_user_id_from_request, login_required
from db import prompts_table


prompts_bp = Blueprint("prompts", __name__)


#GET SPECIFIC PROMPT
def get_specific_prompt(prompt_id):
    response = prompts_table.get_item(
        Key={"prompt_id": prompt_id}
    )

    return response["Item"] #Will return None if not found


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


# DELETE PROMPTS
def delete_prompt_by_id(prompt_id):
    prompts_table.delete_item(Key={'prompt_id': prompt_id})


# --------------------
# Prompts Endpoints
# --------------------


# Obtains either all prompts or filters prompts to obtain all prompts of the same level
@prompts_bp.route("/", methods=["GET"])
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
@prompts_bp.route("/random", methods=["GET"])
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
@prompts_bp.route("/", methods=["POST"])
@login_required
def add_prompt():
    data = request.json
    if "text" not in data or "level" not in data:
        return jsonify({"error": "Missing text or level"}), 400

    user_id = get_user_id_from_request()
    text = data.get("text")
    level = data.get("level")

    prompt_id = create_prompt(text, level, user_id)
    return jsonify({"prompt_id": prompt_id}), 201


# Delete prompt by ID from DynamoDB
@prompts_bp.route("/<id>", methods=["DELETE"])
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

