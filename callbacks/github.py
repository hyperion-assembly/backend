from data_model.models import Project, Contributor, WorkItem, WorkItemStatusEnum, WorkPlace, Treasury
import logging

logger = logging.getLogger(__name__)


def handle_github_event(github_event, action, event_body) -> dict:
    logger.info(f"handle_github_event - github_event {github_event} action {action} event_body {event_body}")

    if github_event == "pull_request":
        if action == "opened":
            workplace = WorkPlace.objects.filter(github_repo_id=event_body["repository"]["id"]).first()
            if not workplace:
                return {"message": "workplace not found"}

            contributor, created = Contributor.objects.get_or_create(
                github_id=event_body["sender"]["id"],
                defaults={"github_username": event_body["sender"]["login"]},
            )
        elif action == "closed":
            is_merged = event_body["pull_request"]["merged"]
            if is_merged:
                # work item is done, set to work_done
                # find out where issue is linked
                work_item = WorkItem.objects.get()
            pass
    elif github_event == "issues":
        if action == "opened":
            workplace = WorkPlace.objects.filter(github_repo_id=event_body["repository"]["id"]).first()
            if not workplace:
                return {"message": "workplace not found"}

            contributor, created = Contributor.objects.get_or_create(
                github_id=event_body["sender"]["id"],
                defaults={"github_username": event_body["sender"]["login"]},
            )
            work_item = WorkItem.objects.create(
                name=event_body["issue"]["title"][:255],
                contributor=contributor,
                workplace=workplace,
                source_url=event_body["issue"]["html_url"],
                github_issue_id=event_body["issue"]["id"],
            )

            return {
                "message": "Work item created successfully",
                "work_item_id": work_item.id,
            }
        elif action == "labeled":
            pass
        elif action == "unlabeled":
            pass
        elif action == "closed":
            workplace = WorkPlace.objects.filter(github_repo_id=event_body["repository"]["id"]).first()
            if not workplace:
                return {"message": "workplace not found"}
            
            issue = event_body["issue"]
            work_item = WorkItem.objects.filter(github_issue_id=issue["id"]).first()

            if issue == 'COMPLETED':
                work_item.status = WorkItemStatusEnum.WORK_DONE
                work_item.save()
            elif issue == 'CANCELED':
                work_item.status = WorkItemStatusEnum.WORK_CANCELED
                work_item.save()
            else:
                logger.info('Issue not closed with status COMPLETED or CANCELED {issue}')
            
    elif github_event == "installation":
        if action == "created":
            owner_id = event_body["sender"]["id"]
            owner, created = Contributor.objects.get_or_create(
                github_id=owner_id, defaults={"github_username": event_body["sender"]["login"]}
            )

            installation = event_body["installation"]
            project_name = installation["account"]["login"]
            project = Project.objects.create(
                name=project_name, source_url=installation["html_url"], description="", owner=owner
            )

            treasury = Treasury.objects.create(name=f"Treasury for {project_name}", project=project)
            repositories = event_body["repositories"]
            workplaces = [
                WorkPlace.objects.create(
                    name=repo["full_name"],
                    project=project,
                    github_repo_id=repo["id"],
                )
                for repo in repositories
            ]
            return {
                "message": "Installation created successfully",
                "project_id": project.id,
                "treasury_id": treasury.id,
                "workplace_ids": [workplace.id for workplace in workplaces],
            }
        elif action == "deleted":
            pass
