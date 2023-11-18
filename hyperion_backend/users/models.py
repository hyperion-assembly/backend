from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for hyperion-backend.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    def get_absolute_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.username})


class Project(models.Model):
    name = models.CharField(_("Name of Project"), blank=True, max_length=255)
    source_url = models.CharField(_("Source URL"), blank=True, max_length=255)
    description = models.CharField(_("Description"), blank=True, max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")


class ProjectContributor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_contributors")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_contributors")


class Treasury(models.Model):
    name = models.CharField(_("Name of Treasury"), blank=True, max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="treasuries")


class Token(models.Model):
    name = models.CharField(_("Name"), blank=True, max_length=255)
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="token")
    status = models.CharField(_("Status"), blank=True, max_length=10)
    onchain_address = models.CharField(_("Onchain Address"), blank=True, max_length=255)
    symbol = models.CharField(_("Symbol"), blank=True, max_length=255)
    total_supply = models.DecimalField(
        _("Total Supply"), max_digits=78, decimal_places=0, blank=True, null=True, help_text=_("Total supply")
    )


class WorkItem(models.Model):
    project_contributor = models.ForeignKey(ProjectContributor, on_delete=models.CASCADE, related_name="work_items")
    source_url = models.CharField(_("Source URL"), blank=True, max_length=255)
    token_amount = models.DecimalField(
        _("Total Supply"), max_digits=78, decimal_places=0, blank=True, null=True, help_text=_("Total supply")
    )
    onchain_transfer_tx = models.CharField(_("Onchain Transfer Tx"), blank=True, max_length=255)
    status = models.CharField(_("Status"), blank=True, max_length=10)
