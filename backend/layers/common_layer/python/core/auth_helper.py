import json
import base64
from decimal import Decimal


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


def json_default(value):
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def format_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS"
        },
        "body": json.dumps(body, default=json_default)
    }