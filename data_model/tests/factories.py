from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from factory import Faker, post_generation
from factory.django import DjangoModelFactory

from data_model.models import Contributor


class ContributorFactory(DjangoModelFactory):
    email = Faker("email")
    github_username = Faker("github_username")
    github_id = Faker("github_id")

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        if create and results and not cls._meta.skip_postgeneration_save:
            # Some post-generation hooks ran, and may have modified us.
            instance.save()

    class Meta:
        model = Contributor
        django_get_or_create = ["username"]
