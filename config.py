import os
from dotenv import load_dotenv
import requests
import boto3

load_dotenv()

REGION = os.getenv("COGNITO_REGION")
USER_POOL_ID = os.getenv("USER_POOL_ID")
CLIENT_ID = os.getenv("CLIENT_ID")


# Load public keys to verify tokens
try:
    JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
    JWKS = requests.get(JWKS_URL).json()["keys"]
except Exception as e:
    JWKS = []
    print("Failed to fetch JWKS:", e)


# Cognito SDK client
cognito_client = boto3.client('cognito-idp', region_name=REGION)
