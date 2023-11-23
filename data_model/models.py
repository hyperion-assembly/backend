from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class WorkPlaceTypeEnum(models.TextChoices):
    GITHUB = "github", _("GitHub")


class WorkItemStatusEnum(models.TextChoices):
    WORK_PENDING = "work_pending", _("Work Pending")
    WORK_CANCELED = "work_canceled", _("Work Canceled")
    WORK_DONE = "work_done", _("Work Done")
    TRANSFER_PENDING = "transfer_pending", _("Transfer Pending")
    TRANSFER_FAILED = "transfer_failed", _("Transfer Failed")
    TRANSFER_DONE = "transfer_done", _("Transfer Done")


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Contributor(BaseModel):
    class Meta:
        verbose_name = "Contributor"
        verbose_name_plural = "Contributors"
        db_table = "contributor"

    email = models.EmailField(_("Email"), blank=True, max_length=255)
    github_username = models.CharField(_("Github Username"), blank=True, max_length=255)
    github_id = models.CharField(_("Github Username"), blank=True, max_length=255)

    def __str__(self):
        return self.github_username or self.email


class Project(BaseModel):
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        db_table = "project"

    name = models.CharField(_("Name of Project"), blank=False, null=False, max_length=255)
    source_url = models.CharField(_("Source URL"), blank=True, max_length=255)
    description = models.CharField(_("Description"), blank=True, max_length=255)
    owner = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name="projects")

    def __str__(self):
        return self.name


class WorkPlace(BaseModel):
    class Meta:
        verbose_name = "Work Place"
        verbose_name_plural = "Work Places"
        db_table = "work_place"

    name = models.CharField(_("Name of Work Place"), blank=False, null=False, max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="work_places")
    github_repo_id = models.CharField(_("Github Repo ID"), blank=True, max_length=255)
    work_place_type = models.CharField(
        _("Work Place Type"),
        blank=True,
        max_length=16,
        choices=WorkPlaceTypeEnum.choices,
        default=WorkPlaceTypeEnum.GITHUB,
    )

    def __str__(self):
        return self.name


class Treasury(BaseModel):
    class Meta:
        verbose_name = "Treasury"
        verbose_name_plural = "Treasuries"
        db_table = "treasury"

    name = models.CharField(_("Name of Treasury"), blank=True, max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="treasuries")
    address = models.CharField(
        _("Address"), 
        blank=True, 
        max_length=42, 
        help_text=_("EVM compatible onchain address in hexadecimal format, e.g., 0xc93e3....8a5d")
    )

    def __str__(self):
        return self.name


class Token(BaseModel):
    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
        db_table = "token"

    name = models.CharField(_("Name"), blank=True, max_length=255)
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="token")
    status = models.CharField(_("Status"), blank=True, max_length=10)
    onchain_address = models.CharField(_("Onchain Address"), blank=True, max_length=255)
    symbol = models.CharField(_("Symbol"), blank=True, max_length=255)
    total_supply = models.DecimalField(
        _("Total Supply"), max_digits=78, decimal_places=0, blank=True, null=True, help_text=_("Total supply")
    )

    def __str__(self):
        return f"{self.symbol} - {self.name} - {self.status}"


class WorkItem(BaseModel):
    class Meta:
        verbose_name = "Work Item"
        verbose_name_plural = "Work Items"
        db_table = "work_item"

    name = models.CharField(_("Name of Work Item"), blank=False, null=False, max_length=255)
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name="work_items", null=True, blank=True)
    workplace = models.ForeignKey(WorkPlace, on_delete=models.CASCADE, related_name="work_items")
    source_url = models.CharField(_("Source URL"), blank=True, max_length=255)
    github_issue_id = models.CharField(_("Github Issue ID"), blank=True, max_length=255)

    token_amount = models.DecimalField(
        _("Total Amount"), max_digits=78, decimal_places=0, blank=True, null=True, help_text=_("Total amount")
    )
    onchain_transfer_tx = models.CharField(_("Onchain Transfer Tx"), blank=True, max_length=255)

    status = models.CharField(
        _("Status"),
        max_length=16,
        choices=WorkItemStatusEnum.choices,
        default=WorkItemStatusEnum.WORK_PENDING,
    )

    def __str__(self):
        return f"{self.workplace}:{self.contributor}: {self.name} - {self.status}"
