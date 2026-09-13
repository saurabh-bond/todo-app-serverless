import json
import os
import boto3
from botocore.exceptions import ClientError
from core.auth_helper import format_response

cognito_client = boto3.client("cognito-idp")
USER_POOL_ID = os.environ.get("USER_POOL_ID")
CLIENT_ID = os.environ.get("USER_POOL_CLIENT_ID")

def lambda_handler(event, context):
    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method")

    if method == "OPTIONS":
        return format_response(200, {})

    try:
        body = json.loads(event.get("body", "{}")) if event.get("body") else {}
    except Exception:
        return format_response(400, {"error": "Invalid JSON payload"})

    try:
        # 1. Sign Up
        if path.endswith("/auth/register") and method == "POST":
            email = body["email"]
            password = body["password"]

            res = cognito_client.sign_up(
                ClientId=CLIENT_ID,
                Username=email,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}]
            )
            return format_response(201, {
                "message": "User registered successfully. Please verify your email.",
                "user_sub": res["UserSub"]
            })

        # 2. Confirm Email
        elif path.endswith("/auth/confirm") and method == "POST":
            email = body["email"]
            code = body["code"]
            cognito_client.confirm_sign_up(
                ClientId = CLIENT_ID,
                Username = email,
                ConfirmationCode = code
            )
            return format_response(200, {"message": "Email verified successfully."})

        # 3. Login (Email + Password Flow)
        elif path.endswith("/auth/login") and method == "POST":
            email = body["email"]
            password = body["password"]
            auth_res = cognito_client.initiate_auth(
                ClientId = CLIENT_ID,
                AuthFlow = "USER_PASSWORD_AUTH",
                AuthParameters = {
                    "USERNAME": email, 
                    "PASSWORD": password
                }
            )
            result = auth_res.get("AuthenticationResult", {})
            return format_response(200, {
                "id_token": result.get("IdToken"),
                "access_token": result.get("AccessToken"),
                "refresh_token": result.get('RefreshToken'),
                "expires_in": result.get("ExpiresIn")
            })

        # 4. Forgot Password (Trigger Code)
        elif path.endswith("/auth/forgot-password") and method == "POST":
            email = body["email"]
            cognito_client.forgot_password(
                ClientId = CLIENT_ID,
                Username = email
            )
            return format_response(200, {"message": "Verification code sent to email."})

        # 5. Confirm Forgot Password
        elif path.endswith("/auth/confirm-forgot-password") and method == "POST":
            email = body["email"]
            code = body["code"]
            new_password = body["new_password"]
            cognito_client.confirm_forgot_password(
                ClientId = CLIENT_ID,
                Username = email,
                ConfirmationCode = code,
                Password = password
            )
            return format_response(200, {"message": "Password reset successfully."})

        return format_response(404, {"error": "Route not found"})

    except ClientError as e: 
        error_msg = e.response["Error"]["Message"]
        return format_response(400, {"error": error_msg})
    except Exception as ex:
        return format_response(500, {"error": str(ex)})

