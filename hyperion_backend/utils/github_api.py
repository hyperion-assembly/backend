import logging
from typing import Union
from django.conf import settings
from github import Auth, GithubIntegration, IssueComment

gi = GithubIntegration(auth=Auth.AppAuth(app_id=settings.GITHUB_APP_ID, private_key=settings.GITHUB_APP_PRIVATE_KEY))


def get_github_sdk_for_repo(repo_path: str):
    app_installation = gi.get_repo_installation(repo_path.split("/")[0], repo_path.split("/")[1])
    return app_installation.get_github_for_installation()


def post_comment_on_issue(repo_path: str, issue_number: str | int, comment: str) -> IssueComment:
    """
    Post a comment on a specific issue in a GitHub repository.

    :param repo_path: The full GitHub repository name in the format "owner/repo_name".
    :param issue_number: The issue_number on which to post the comment, e.g. 2
    :param comment: The content of the comment to post, e.g. "Hello World!"
    """

    github_app = get_github_sdk_for_repo(repo_path)
    repo = github_app.get_repo(repo_path)
    issue = repo.get_issue(number=issue_number)
    return issue.create_comment(comment)
