import json
from typing import List
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
import logging
from hyperion_backend.utils.github_api import post_comment_on_issue
from onchain.ens import normalize_address
from onchain.thirdweb_api import create_token_contract, mint_tokens
from thirdweb.types.currency import TokenAmount
from web3.datastructures import AttributeDict
from web3 import Web3

logger = logging.getLogger(__name__)


class WorkPlaceTypeEnum(models.TextChoices):
    GITHUB = "github", _("GitHub")


class WorkItemStatusEnum(models.TextChoices):
    WORK_PENDING = "work_pending", _("Work Pending")
    WORK_CANCELED = "work_canceled", _("Work Canceled")
    WORK_CONFIRMED = "work_confirmed", _("Work Confirmed")
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
    onchain_address = models.CharField(
        _("Onchain Address"),
        blank=True,
        max_length=42,
        help_text=_("EVM compatible onchain address in hexadecimal format, e.g., 0xc93e3....8a5d"),
    )

    def __str__(self):
        return self.github_username or self.email or self.onchain_address

    @property
    def normalized_address(self) -> str:
        return normalize_address(self.onchain_address)


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
        constraints = [
            models.UniqueConstraint(fields=["github_repo_id"], name="unique_github_repo_id"),
        ]

    name = models.CharField(_("Name of Work Place"), blank=False, null=False, max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="work_places")
    github_repo_id = models.CharField(_("Github Repo ID"), blank=True, max_length=255)
    is_active = models.BooleanField(_("is_active"), default=True)
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
        help_text=_("EVM compatible onchain address in hexadecimal format, e.g., 0xc93e3....8a5d"),
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
    onchain_address = models.CharField(_("Onchain Address"), blank=True, max_length=255)
    symbol = models.CharField(_("Symbol"), blank=True, max_length=255)
    total_supply = models.DecimalField(
        _("Total Supply"), max_digits=78, decimal_places=0, blank=True, null=True, help_text=_("Total supply")
    )

    def __str__(self):
        return f"{self.symbol} - {self.name}"

    def create_onchain_contract(self):
        res = create_token_contract(self.name, self.symbol, self.total_supply, None)
        logger.info(f"create_onchain_contract - res: {res}")
        self.save()

    def mint(self, token_amounts: list[TokenAmount]) -> AttributeDict:
        return mint_tokens(self.onchain_address, token_amounts)


class WorkItem(BaseModel):
    class Meta:
        verbose_name = "Work Item"
        verbose_name_plural = "Work Items"
        db_table = "work_item"

    name = models.CharField(_("Name of Work Item"), blank=False, null=False, max_length=255)
    contributors = models.ManyToManyField(
        Contributor, related_name="work_items", db_table="contributors_to_work_items", blank=True
    )
    workplace = models.ForeignKey(WorkPlace, on_delete=models.CASCADE, related_name="work_items")
    source_url = models.CharField(_("Source URL"), blank=True, max_length=255)
    github_issue_id = models.CharField(_("Github Issue ID"), blank=True, max_length=255)
    data = models.JSONField(_("Data"), blank=True, null=True)
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
        return f"{self.workplace}: {self.name} - {self.status}"

    def distribute_tokens(self):
        if not self.workplace.project.token:
            logger.info(f"no token for project {self.workplace.project.id}")
            return

        self.status = WorkItemStatusEnum.TRANSFER_PENDING
        self.save()

        contributors = self.contributors.all()
        if not all(contributor.onchain_address for contributor in contributors):
            self.status = WorkItemStatusEnum.TRANSFER_FAILED
            self.save()
            return

        token_amount_split = self.token_amount / len(contributors)
        token_amounts = [
            TokenAmount(contributor.normalized_address, token_amount_split) for contributor in contributors
        ]
        token = self.workplace.project.token
        did_mint = False
        try:
            contributor_names = ", ".join(
                [f"@{contributor}" for contributor in contributors.values_list("github_username", flat=True)]
            )
            post_comment_on_issue(
                self.workplace.name,
                self.data["issue"]["number"],
                f"I'm starting to distribute {self.token_amount} {token.symbol} tokens for this to: {contributor_names}",
            )

            tx_data = token.mint(token_amounts)
            did_mint = True

            tx_data = json.loads(Web3.toJSON(tx_data))
            self.data["tx_data"] = tx_data
            self.status = WorkItemStatusEnum.TRANSFER_DONE
            self.save()

            tx_url = f"https://goerli.etherscan.io/tx/{tx_data['transactionHash']}"
            post_comment_on_issue(
                self.workplace.name,
                self.data["issue"]["number"],
                f"Hyperion distributed {self.token_amount} {token.symbol} tokens to {len(contributors)} contributor{'s' if len(contributors) else ''}: {tx_url}",
            )
        except Exception as e:
            error_msg = f"error - but tokens were minted: {e}" if did_mint else f"Error minting tokens: {e}"
            logger.error(f"work item {self.id} {error_msg}")
            if not did_mint:
                self.status = WorkItemStatusEnum.TRANSFER_FAILED
                self.save()

            post_comment_on_issue(
                self.workplace.name,
                self.data["issue"]["number"],
                error_msg,
            )
            return

        self.status = WorkItemStatusEnum.TRANSFER_DONE
        self.save()
