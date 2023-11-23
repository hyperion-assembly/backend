import pytest

from data_model.models import Contributor
from data_model.tests.factories import ContributorFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def contributor(db) -> Contributor:
    return ContributorFactory()
