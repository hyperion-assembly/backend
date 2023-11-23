import json

from django.contrib import admin
from django.utils.html import format_html
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from data_model.models import Contributor, Project, WorkItem, WorkPlace, Token, Treasury


def get_pretty_data(data: dict) -> str:
    data_str = json.dumps(data, sort_keys=True, indent=2)
    formatter = HtmlFormatter(style="colorful")
    return format_html(highlight("{}", JsonLexer(), formatter), data_str)


class HyperionAdminSite(admin.AdminSite):
    enable_nav_sidebar = False
    site_header = "Hyperion admin 🤩"


admin_site = HyperionAdminSite(name="hyperion-admin")


admin_site.register(Contributor)
admin_site.register(Project)
admin_site.register(WorkPlace)
admin_site.register(WorkItem)
admin_site.register(Token)
admin_site.register(Treasury)
