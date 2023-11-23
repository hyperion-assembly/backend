import json

import hmac
from hashlib import sha1
import logging

from django.http import HttpRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from callbacks.github import handle_github_event

logger = logging.getLogger(__name__)


def get_request_body_signature(key, body):
    return f"sha1={hmac.new(key.encode(), body.encode(), sha1).hexdigest()}"


@csrf_exempt
def github_callback(request: HttpRequest):
    logger.info(f"github callback - headers {request.headers} body {request.body}")
    err_msg = None

    token = settings.GITHUB_WEBHOOK_SECRET
    if not isinstance(token, str):
        err_msg = "Must provide a 'GITHUB_WEBHOOK_SECRET' env variable"
        return JsonResponse({"message": err_msg}, status=401)

    sig = request.headers.get("X-Hub-Signature")
    if not sig:
        err_msg = "No X-Hub-Signature found on request"
        return JsonResponse({"message": err_msg}, status=401)

    github_event = request.headers.get("X-GitHub-Event")
    if not github_event:
        err_msg = "No X-Github-Event found on request"
        return JsonResponse({"message": err_msg}, status=422)

    id = request.headers.get("X-GitHub-Delivery")
    if not id:
        err_msg = "No X-Github-Delivery found on request"
        return JsonResponse({"message": err_msg}, status=401)

    calculated_sig = get_request_body_signature(token, request.body.decode("utf-8"))
    if sig != calculated_sig:
        err_msg = "X-Hub-Signature incorrect. Github webhook token doesn't match"
        return JsonResponse({"message": err_msg}, status=401)

    event_body = json.loads(request.body.decode("utf-8"))
    action = event_body.get("action")
    print("---------------------------------")
    print(f'Github-Event: "{github_event}" with action: "{action}"')
    print("---------------------------------")
    print("Payload", event_body)

    handle_github_event(github_event, action, event_body)

    response = {
        "body": json.dumps(
            {
                "input": event_body,
            }
        ),
    }

    return JsonResponse(response, status=200)
