from functools import wraps
from flask import request, session, jsonify, abort
from jose import jwt
from config import JWKS, CLIENT_ID, REGION, USER_POOL_ID


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
        audience=CLIENT_ID, 
        issuer=f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
    )
    return claims


