from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DataModelConfig(AppConfig):
    name = "data_model"

    def ready(self):
        try:
            import data_model.signals  # noqa: F401
        except ImportError:
            pass
