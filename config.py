import os
from dotenv import load_dotenv
import requests

load_dotenv()

REGION = os.getenv("COGNITO_REGION")
USER_POOL_ID = os.getenv("USER_POOL_ID")
CLIENT_ID = os.getenv("CLIENT_ID")

# Load public keys to verify tokens
JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
JWKS = requests.get(JWKS_URL).json()["keys"]

# Cognito SDK client
cognito_client = boto3.client('cognito-idp', region_name=os.getenv('COGNITO_REGION'))
