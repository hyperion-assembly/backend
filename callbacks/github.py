import json

import hmac
import os
from hashlib import sha1


def sign_request_body(key, body):
    return f"sha1={hmac.new(key.encode(), body.encode(), sha1).hexdigest()}"


def github_webhook_listener(event, context):
    err_msg = None
    token = os.environ.get("GITHUB_WEBHOOK_SECRET")
    headers = event.get("headers")
    sig = headers.get("X-Hub-Signature")
    github_event = headers.get("X-GitHub-Event")
    id = headers.get("X-GitHub-Delivery")
    calculated_sig = sign_request_body(token, event.get("body"))

    if not isinstance(token, str):
        err_msg = "Must provide a 'GITHUB_WEBHOOK_SECRET' env variable"
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "text/plain"},
            "body": err_msg,
        }

    if not sig:
        err_msg = "No X-Hub-Signature found on request"
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "text/plain"},
            "body": err_msg,
        }

    if not github_event:
        err_msg = "No X-Github-Event found on request"
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "text/plain"},
            "body": err_msg,
        }

    if not id:
        err_msg = "No X-Github-Delivery found on request"
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "text/plain"},
            "body": err_msg,
        }

    if sig != calculated_sig:
        err_msg = "X-Hub-Signature incorrect. Github webhook token doesn't match"
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "text/plain"},
            "body": err_msg,
        }
    print("Github-Event", event)
    event_body = json.loads(event.get("body"))
    action = event_body.get("action")
    print("---------------------------------")
    print(f'Github-Event: "{github_event}" with action: "{action}"')
    print("---------------------------------")
    print("Payload", event_body)

    response = {
        "statusCode": 200,
        "body": json.dumps(
            {
                "input": event,
            }
        ),
    }

    return response
