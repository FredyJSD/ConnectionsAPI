from flask import Blueprint, request, jsonify
from utils import get_user_id_from_request, login_required
from db import sessions_table
from prompts import get_all_admin_prompts, get_all_user_prompts
from datetime import datetime
import random

sessions_bp = Blueprint("sessions", __name__)

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
def get_session_id(session_id):
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
# Session Endpoints
# --------------------


@sessions_bp.route("/sessions/new/<session_id>", methods=["POST"])
@login_required
def sessions(session_id):
    level = request.args.get("level")
    user_id = get_user_id_from_request()
    prompts = session_prompts(user_id, level)
    create_session(user_id, session_id, prompts)
    return jsonify({"session_id": session_id}), 201



@sessions_bp.route("/sessions/<session_id>", methods=["GET"])
@login_required
def get_session(session_id):
    return get_session_prompts(session_id)


@sessions_bp.route("/sessions/<session_id>/respond", methods=["POST"])
@login_required
def respond(session_id):
    data = request.json
    return prompt_response(session_id, data)


@sessions_bp.route("/sessions/<session_id>", methods=["DELETE"])
@login_required
def delete_session(session_id):
    session_to_delete = get_session_id(session_id)

    if not session_to_delete:
        return jsonify({"error": "Prompt doesn't exist"}), 404
    
    user_id = get_user_id_from_request()

    if user_id != session_to_delete["user_id"]:
        return jsonify({"error": "User doesn't have permission"}), 403
    
    delete_session_record(session_id)
    return jsonify({"message": f"Success: Session {session_id} deleted"}), 200