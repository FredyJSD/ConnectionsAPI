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

