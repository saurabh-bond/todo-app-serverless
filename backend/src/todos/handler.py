import json
import os
import uuid
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone
from core.auth_helper import get_user_context, format_response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method")
    path_params = event.get("pathParameters") or {}
    user = get_user_context(event)

    if method == "OPTIONS":
        return format_response(200, {})

    # GET ALL TODOS (Open to logged in users)
    if method == "GET":
        response = table.query(
            KeyConditionExpression = Key("PK").eq(f"USER#{user['user_id']}") & Key("SK").begins_with("TODO#")
        )

        return format_response(200, {"todos": response.get("Items", [])})

    elif method == "POST":
        body = json.loads(event.get("body", "{}"))
        todo_title = body.get("todo_title", "Todo")
        todo_desc = body.get("description", "")
        todo_id = str(uuid.uuid4())
        current_time_epoch = int(datetime.now(timezone.utc).timestamp())
        print(f"current_time: {current_time_epoch}")

        item = {
            "PK": f"USER#{user['user_id']}",
            "SK": f"TODO#{todo_id}",
            "GSI1PK": "STATUS#PENDING",
            "GSI1SK": f"CREATED_AT#{current_time_epoch}",
            "title": todo_title,
            "description": todo_desc,
            "status": "PENDING",
            "created_at": current_time_epoch
        }
        table.put_item(Item = item)
        return format_response(201, {"message": "Todo task created successfully.", "todo": item})

    elif method == "DELETE":
        todo_id = path_params.get("todo_id")
        table.delete_item(
            Key={
                "PK": f"USER#{user['user_id']}",
                "SK": f"TODO#{todo_id}"
            }
        )
        return format_response(200, {"message": "Todo task dropped successfully."})

    return format_response(404, {"error": "Route not found."})
    