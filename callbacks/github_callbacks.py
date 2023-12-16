import logging
import re
from data_model.models import Project, Contributor, WorkItem, WorkItemStatusEnum, WorkPlace, Treasury
from django.db import transaction
from django.conf import settings

from hyperion_backend.utils.github_api import post_comment_on_issue

logger = logging.getLogger(__name__)


def handle_github_event(github_event, action, event_body) -> dict:
    logger.info(f"handle_github_event - github_event: {github_event} action: {action}")

    if github_event == "pull_request":
        if action == "opened":
            pass
        elif action == "closed":
            pass
    elif github_event == "issues":
        issue = event_body["issue"]

        if action == "opened" or action == "labeled":
            has_hyperion_label = any(label.get("name") for label in issue.get("labels", {}))
            if not has_hyperion_label:
                return {"message": "issue not labeled with hyperion"}

            workplace = WorkPlace.objects.filter(github_repo_id=event_body["repository"]["id"]).first()
            if not workplace:
                return {"message": "workplace not found"}

            contributor, created = Contributor.objects.get_or_create(
                github_id=event_body["sender"]["id"],
                defaults={"github_username": event_body["sender"]["login"]},
            )
            work_item, created = WorkItem.objects.get_or_create(
                name=event_body["issue"]["title"][:255],
                workplace=workplace,
                source_url=event_body["issue"]["html_url"],
                github_issue_id=event_body["issue"]["id"],
                defaults={"data": {"issue": event_body["issue"]}, "token_amount": 0},
            )

            post_comment_on_issue(
                workplace.name,
                issue["number"],
                f"Hyperion registered this issue successfully 🙏🏼",
            )

            return {
                "message": "work item created successfully",
                "work_item_id": work_item.id,
            }
        elif action == "unlabeled":
            pass
        elif action == "assigned":
            assignee = issue["assignee"]
            if not assignee:
                return {"message": "issue not assigned to anyone"}

            contributor, created = Contributor.objects.get_or_create(
                github_id=assignee["id"],
                defaults={"github_username": assignee["login"]},
            )
            work_item = WorkItem.objects.filter(github_issue_id=issue["id"]).first()
            if not work_item:
                return {"message": f"no work item found for issue {issue['id']}"}

            work_item.contributors.add(contributor)
            work_item.save()

            return {
                "message": f"contributor {contributor.github_username} added to work item {work_item.id}",
                "work_item_id": str(work_item.id),
            }
        elif action == "unassigned":
            assignee = event_body["assignee"]
            contributor, created = Contributor.objects.get_or_create(
                github_id=assignee["id"],
                defaults={"github_username": assignee["login"]},
            )
            work_item = WorkItem.objects.filter(github_issue_id=issue["id"]).first()
            work_item.contributors.remove(contributor)
            work_item.save()

            return {
                "message": f"contributor {contributor.github_username} removed from work item {work_item.id}",
                "work_item_id": str(work_item.id),
            }
        elif action == "closed":
            has_hyperion_label = any(label.get("name") for label in issue.get("labels", {}))
            if not has_hyperion_label:
                return {"message": "issue not labeled with hyperion"}

            repo_id = event_body["repository"]["id"]
            workplace = WorkPlace.objects.filter(github_repo_id=repo_id).first()
            if not workplace:
                return {"message": f"no workplace found for repo {repo_id}"}

            work_item = WorkItem.objects.filter(github_issue_id=issue["id"]).first()
            if not work_item:
                return {"message": f"no work item found for issue {issue['id']}"}

            close_reason = issue["state_reason"]
            if close_reason == "completed":
                work_item.status = WorkItemStatusEnum.WORK_DONE
                work_item.save()

                has_contributors = work_item.contributors.exists()
                if not has_contributors:
                    return {"message": f"no contributors for work item {work_item.id}"}

                work_item.distribute_tokens()

            elif close_reason == "canceled":
                work_item.status = WorkItemStatusEnum.WORK_CANCELED
                work_item.save()
            else:
                logger.info(f"Issue not closed with status COMPLETED or CANCELED {issue}")
    elif github_event == "issue_comment":
        issue = event_body["issue"]
        has_hyperion_label = any(label.get("name") for label in issue.get("labels", {}))
        if not has_hyperion_label:
            return {"message": "issue not labeled with hyperion"}

        is_hyperion_bot_comment = event_body["sender"]["login"] == "hyperion-assembly[bot]"
        if is_hyperion_bot_comment:
            return {"message": "skip comment from hyperion bot"}

        comment = event_body["comment"]
        body = comment["body"]
        if not body.lower().startswith("@hyperion"):
            return {"message": "comment not directed at hyperion"}

        if action == "created" or action == "edited":
            # "body": "@hyperion-assembly this is worth 5 tokens",
            work_item = WorkItem.objects.filter(github_issue_id=issue["id"]).first()
            if not work_item:
                return {"message": "work item not found"}

            # regex to find token value in body
            r = re.compile(r"(\d+)").search(body)
            if not r:
                return {"message": "no token value found in comment"}

            token_value = r.group(1)
            work_item.token_amount = token_value
            work_item.save()

            token_symbol = work_item.workplace.project.token.symbol if work_item.workplace.project.token else ""
            post_comment_on_issue(
                work_item.workplace.name,
                issue["number"],
                f"Hyperion will distribute {token_value} {token_symbol} tokens when this is completed",
            )

            return {
                "message": f"updated token value {token_value} for work item {work_item.id}",
                "work_item_id": str(work_item.id),
            }
        elif action == "deleted":
            pass
    elif github_event == "installation_repositories":
        logger.info(f"installation_repositories - event_body: {event_body}")
        if action == "added":
            project = Project.objects.filter(name=event_body["installation"]["account"]["login"]).first()

            add_repositories = event_body["repositories_added"]

            remove_repositories = event_body["repositories_removed"]

            if add_repositories:
                [
                    WorkPlace.objects.get_or_create(
                        name=repo["full_name"],
                        project=project,
                        github_repo_id=repo["id"],
                    )
                    for repo in add_repositories
                ]
            if remove_repositories:
                remove_repo_ids = [repo["id"] for repo in remove_repositories]
                WorkPlace.objects.filter(project=project, github_repo_id__in=remove_repo_ids).update(is_active=False)
        elif action == "removed":
            pass
    elif github_event == "installation":
        if action == "created":
            owner_id = event_body["sender"]["id"]
            owner, _ = Contributor.objects.get_or_create(
                github_id=owner_id, defaults={"github_username": event_body["sender"]["login"]}
            )
            installation = event_body["installation"]
            project_name = installation["account"]["login"]

            with transaction.atomic():
                project, _ = Project.objects.get_or_create(
                    name=project_name,
                    source_url=installation["html_url"],
                    owner=owner,
                    defaults={
                        "description": "",
                    },
                )

                treasury = Treasury.objects.create(name=f"Treasury for {project_name}", project=project)
                repositories = event_body["repositories"]
                workplaces = WorkPlace.objects.bulk_create(
                    [
                        WorkPlace(
                            name=repo["full_name"],
                            project=project,
                            github_repo_id=repo["id"],
                            is_active=True,
                        )
                        for repo in repositories
                    ],
                    update_conflicts=True,
                    unique_fields=["github_repo_id"],
                    update_fields=["is_active", "project_id", "name"],
                )
                return {
                    "message": "Installation created successfully",
                    "project_id": str(project.id),
                    "treasury_id": str(treasury.id),
                    "workplace_ids": [str(workplace.id) for workplace in workplaces],
                }
        elif action == "deleted":
            pass

    return {}
