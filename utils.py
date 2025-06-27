from functools import wraps
from flask import request, session, jsonify, abort
from auth import verify_token


# LOGIN REQUIRED DECORATOR
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return f(*args, **kwargs)

        authorization_header = request.headers.get("Authorization", "")
        token = authorization_header.replace("Bearer ", "")

        if not token:
            return jsonify({"error": "Missing access token"}), 401

        try:
            claims = verify_token(token)
            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Authentication required"}), 401

    return decorated_function


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

