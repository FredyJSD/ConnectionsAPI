### Learning Log Entry: Cognito JWT Verification in Flask ###
## Authenticating and Verifying Users Using AWS Cognito JWTs in a Flask API ##
# Key Concepts #
- Cognito Client
    - Use boto3.client('cognito-idp')
        - Sign up users
        - Log them in (initiate auth)
        - Manage tokens

- JWT (JSON Web Tokens)
    - Cryptographically signed tokens that represent a user's identity when signed in
    - JWTs contain "claims":
        - 'sub': user's unique ID in Cognito
        - 'email': if requested in scopes
        - 'exp': expiration time (Unix timestamp)
        - 'aud': audience (should match 'CLIENT_ID')
    - Every JWT consists of 3 parts
        - header.payload.signature
    - JWT Authorization
        - In HTTP APIs, tokens are sent in the request header
            - Authorization: Bearer <token>
    - To verify and decode, must provide issuer
- JWKS
    - Public keys provided by AWS Cognito to verify JWT signatures
    - Must match the user kid (Key ID) with the Cognito public keys (JWKS)
- To get JWKS (Python)
    - JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
    - JWKS = requests.get(JWKS_URL).json()["keys"]

- ID Token vs Access Token
    - 'id_token': Contains user identity information (email, sub, etc.)
        - Used for client-side identity verification (e.g., /auth/me)
    - 'access_token': Used for authorizing access to protected resources (e.g., /prompts, /sessions)

- Verifying JWTs in Flask
    - Use 'python-jose' (e.g., 'from jose import jwt')
    - Match token's 'kid' in header to 'JWKS' key
    - Decode using 'jwt.decode(token, key, algorithms, audience, issuer)'
    - Raise 'JWTError' if invalid token or signature

- Flask Authorization Decorator
    - Create a '@login_required' decorator
        - Extracts token from 'Authorization' header
        - Verifies token
        - Aborts request with 401 if invalid or missing

- Token Usage Flow
    - Login returns both 'access_token' and 'id_token'
    - Send 'access_token' in headers for protected endpoints
    - Use 'id_token' for identity-based endpoints like '/auth/me'

- Common Issues and Fixes
    - 'NotAuthorizedException': Invalid login credentials
    - 'UserNotConfirmedException': Email not verified
    - Always catch and return meaningful auth errors
    - Circular import issues: separate JWT logic from 'auth.py'

- Environment Security
    - Never hardcode secret values
    - Use '.env' with 'dotenv.load_dotenv()'
    - Store 'CLIENT_ID', 'USER_POOL_ID', 'REGION' safely

- Zappa Setup:
    - Installed and configured Zappa.
    - zappa init to create zappa_settings.json.
    - zappa deploy dev for initial deployment.
    - Added env varibales in Zappa config

- Error Codes
    - 400: Bad request
    - 401: Unauthorized
    - 403: Forbidden
    - 404: Not found
