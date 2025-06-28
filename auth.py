from flask import Blueprint, request, jsonify, session, abort
from jose import jwt
import boto3
import requests
from config import REGION, USER_POOL_ID, CLIENT_ID, JWKS
from utils import login_required, verify_token

auth_bp = Blueprint("auth", __name__)
cognito_client = boto3.client('cognito-idp', region_name=REGION)


# Register New User 
def register_user(username, email, password):
    try:
        cognito_client.sign_up(
            ClientId=CLIENT_ID,
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
            ClientId = CLIENT_ID,
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

    except cognito_client.exceptions.UserNotConfirmedException:
        return {"error": "Email not verified. Please check your inbox to confirm your account."}, 403

    except cognito_client.exceptions.NotAuthorizedException:
        return {"error": "Incorrect email or password."}, 403

    except cognito_client.exceptions.UserNotFoundException:
        return {"error": "User does not exist."}, 404

    except Exception as e:
        return {"error": f"Login failed: {str(e)}"}, 500


# --------------------
# Auth Endpoints
# --------------------


@auth_bp.route('/register', methods=["POST"])
def register():
    data = request.json
    result = register_user(data["username"], data["email"], data["password"])
    return jsonify(result)


@auth_bp.route('/login', methods=["POST"])
def login():
    data = request.json
    result = login_user(data["email"], data["password"])

    if isinstance(result, tuple): 
        return jsonify(result[0]), result[1]

    return jsonify(result)


@auth_bp.route("/me", methods=["GET"])
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
    except Exception as e:
        print(f"[TOKEN ERROR] {str(e)}")
        return jsonify({"error": "Invalid token"}), 401


@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return jsonify("User Logged Out")

