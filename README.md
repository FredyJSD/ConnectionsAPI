README: ConnectionsAPI

Project Overview
ConnectionsAPI is a RESTful API built with Flask that allows users to manage conversation prompts 
and organize them into interactive sessions. It includes secure authentication with AWS Cognito and 
uses DynamoDB for scalable NoSQL data storage.

Tech
- Backend: Python, Flask
- Database: AWS DynamoDB (NoSQL)
- Authentication: AWS Cognito (JWT-based)
- Deployment: AWS Lambda + API Gateway
- Testing: Postman

Authentication
This API uses AWS Cognito for user registration and JWT-based token authentication. 
You must first register and log in to access protected endpoints.

API Usage

Register

    POST /register
    {
    "username": "user123",
    "email": "user@example.com",
    "password": "YourPassword123!"
    }

    Returns a message prompting email verification.

Login

    POST /login
    {
    "email": "user@example.com",
    "password": "YourPassword123!"
    }

    Returns an access_token to be used in the Authorization header, and id_token for GET /auth/me

    {
    "access_token": "eyJraWQiOiJ...",
    "id_token": "eyJhbGciOiJI..."
    }

Get Logged-In User Info
    
    GET /auth/me
    Header: Authorization: Bearer <id_token>

    returns
    {
    "user_id": "abc-123-uuid",
    "email": "user@example.com"
    }

Authenticated Header Format

    Authorization: Bearer <access_token>

Prompts Endpoints

Create a Prompt

    POST /prompts
    Headers: Authorization required

    {
    "text": "What is the capital of France?",
    "level": 1
    }

    Returns: prompt_id

Get All Prompts (optional level filter)

    GET /prompts
    Headers: Authorization required
    Optional: ?level=ice

    Returns: All admin + user prompts

Delete a Prompt

    DELETE /prompts/<prompt_id>
    Headers: Authorization required

    Only prompt owner can delete

Sessions Endpoints

Create a Session (optional level filter)

    POST /sessions
    Headers: Authorization required
    Optional: ?level=ice
    Randomly selects a pool of prompts and creates a session.

View Session

    GET /sessions/<session_id>
    Headers: Authorization required

    Returns list of prompts for the session

Submit a Response

    POST /sessions/<session_id>/respond
    Headers: Authorization required
    {
    "prompt_id": "<prompt_id>",
    "response": "My response here"
    }
    Stores response for the given prompt

Delete a Session

    DELETE /sessions/<session_id>
    Header: Authorization required

    Only the session owner can delete
