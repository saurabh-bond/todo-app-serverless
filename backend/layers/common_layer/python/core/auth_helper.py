import json
import base64 

def get_user_context(event: dict) -> dict:
    """Extract user information and roles from the API Gateway Authorizer context."""
    try:
        claims = event['requestContext']['authorizer']['jwt']['claims']
        return {
            "user_id": claims.get('sub'),
            "email": claims.get('email')
        }
    except (KeyError, TypeError):
        return {
            "user_id": None,
            "email": None
        }

def format_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS"
        },
        "body": json.dumps(body)
    }