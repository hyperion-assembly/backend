from django.test import TestCase, RequestFactory
from django.http import HttpRequest
from callbacks.views import github_callback
from unittest.mock import patch

import logging

logger = logging.getLogger(__name__)

installation_created_payload = {
    "action": "created",
    "installation": {
        "id": 123,
        "account": {
            "login": "hyperion-assembly",
            "id": 1234,
            "node_id": "O_1",
            "avatar_url": "https://avatars.githubusercontent.com/u/150948975?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/hyperion-assembly",
            "html_url": "https://github.com/hyperion-assembly",
            "followers_url": "https://api.github.com/users/hyperion-assembly/followers",
            "following_url": "https://api.github.com/users/hyperion-assembly/following{/other_user}",
            "gists_url": "https://api.github.com/users/hyperion-assembly/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/hyperion-assembly/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/hyperion-assembly/subscriptions",
            "organizations_url": "https://api.github.com/users/hyperion-assembly/orgs",
            "repos_url": "https://api.github.com/users/hyperion-assembly/repos",
            "events_url": "https://api.github.com/users/hyperion-assembly/events{/privacy}",
            "received_events_url": "https://api.github.com/users/hyperion-assembly/received_events",
            "type": "Organization",
            "site_admin": False,
        },
        "repository_selection": "all",
        "access_tokens_url": "https://api.github.com/app/installations/44332092/access_tokens",
        "repositories_url": "https://api.github.com/installation/repositories",
        "html_url": "https://github.com/organizations/hyperion-assembly/settings/installations/44332092",
        "app_id": 1234,
        "app_slug": "hyperion-assembly",
        "target_id": 1234,
        "target_type": "Organization",
        "permissions": {"issues": "write", "metadata": "read", "pull_requests": "read"},
        "events": ["issues", "issue_comment", "label", "pull_request", "repository"],
        "created_at": "2023-12-23T11:09:45.000+01:00",
        "updated_at": "2023-12-23T11:09:45.000+01:00",
        "single_file_name": None,
        "has_multiple_single_files": False,
        "single_file_paths": [],
        "suspended_by": None,
        "suspended_at": None,
    },
    "repositories": [
        {"id": 123, "node_id": "R_1", "name": "backend", "full_name": "hyperion-assembly/backend", "private": True},
        {"id": 124, "node_id": "R_2", "name": ".github", "full_name": "hyperion-assembly/.github", "private": False},
        {"id": 125, "node_id": "R_3", "name": "frontend", "full_name": "hyperion-assembly/frontend", "private": True},
    ],
    "requester": None,
    "sender": {
        "login": "hellno",
        "id": 686075,
        "node_id": "MDQ6VXNlcjY4NjA3NQ==",
        "avatar_url": "https://avatars.githubusercontent.com/u/686075?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/hellno",
        "html_url": "https://github.com/hellno",
        "followers_url": "https://api.github.com/users/hellno/followers",
        "following_url": "https://api.github.com/users/hellno/following{/other_user}",
        "gists_url": "https://api.github.com/users/hellno/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/hellno/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/hellno/subscriptions",
        "organizations_url": "https://api.github.com/users/hellno/orgs",
        "repos_url": "https://api.github.com/users/hellno/repos",
        "events_url": "https://api.github.com/users/hellno/events{/privacy}",
        "received_events_url": "https://api.github.com/users/hellno/received_events",
        "type": "User",
        "site_admin": False,
    },
}


class GithubCallbackTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("callbacks.views.get_request_body_signature")
    def test_github_callback(self, mock_signature):
        mock_signature.return_value = "sha1=abc123"
        request = HttpRequest()
        request.method = "POST"
        request.META = {
            "HTTP_X_HUB_SIGNATURE": "sha1=abc123",
            "HTTP_X_GITHUB_EVENT": "push",
            "HTTP_X_GITHUB_DELIVERY": "delivery_id",
        }
        request._body = b'{"action": "opened"}'

        response = github_callback(request)
        logger.info(f"github callback response: {response.content}")
        self.assertEqual(response.status_code, 200)

    def test_handleGithubEvent_installationCreated_success(self):
        pass
