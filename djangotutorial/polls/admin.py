from typing import TYPE_CHECKING

from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

if TYPE_CHECKING:
    from django.db import models
    from django.http import HttpRequest

action_names = {
    ADDITION: pgettext_lazy("logentry_admin:action_type", "Addition"),
    DELETION: pgettext_lazy("logentry_admin:action_type", "Deletion"),
    CHANGE: pgettext_lazy("logentry_admin:action_type", "Change"),
}


class ActionListFilter(admin.SimpleListFilter):
    title = _("action")
    parameter_name = "action_flag"

    def lookups(
        self,
        request: "HttpRequest",  # noqa: ARG002
        model_admin: "models.QuerySet[LogEntry]",  # noqa: ARG002
    ) -> list[tuple[int, str]]:
        return action_names.items()

    def queryset(
        self,
        request: "HttpRequest",  # noqa: ARG002
        queryset: "models.QuerySet[LogEntry]",
    ) -> "models.QuerySet[LogEntry]":
        if self.value():
            queryset = queryset.filter(action_flag=self.value())
        return queryset


class UserListFilter(admin.SimpleListFilter):
    title = _("staff user")
    parameter_name = "user"

    def lookups(
        self,
        request: "HttpRequest",  # noqa: ARG002
        model_admin: "LogEntryAdmin",  # noqa: ARG002
    ) -> list[tuple[int, str]]:
        staff = get_user_model().objects.filter(is_staff=True)
        return ((s.pk, force_str(s)) for s in staff)

    def queryset(
        self,
        request: "HttpRequest",  # noqa: ARG002
        queryset: "models.QuerySet[LogEntry]",
    ) -> "models.QuerySet[LogEntry]":
        if self.value():
            queryset = queryset.filter(
                user_id=self.value(), user__is_staff=True)
        return queryset


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = "action_time"

    readonly_fields = [f.name for f in LogEntry._meta.fields] + [  # noqa: SLF001
        "object_link",
        "action_description",
        "user_link",
        "get_change_message",
    ]

    fieldsets = (
        (
            _("Metadata"),
            {
                "fields": (
                    "action_time",
                    "user_link",
                    "action_description",
                    "object_link",
                )
            },
        ),
        (
            _("Details"),
            {
                "fields": (
                    "get_change_message",
                    "content_type",
                    "object_id",
                    "object_repr",
                )
            },
        ),
    )

    list_filter = (
        UserListFilter,
        "content_type",
        ActionListFilter,
    )

    search_fields = (
        "object_repr",
        "change_message",
    )

    list_display_links = (
        "action_time",
        "get_change_message",
    )
    list_display = (
        "action_time",
        "user_link",
        "content_type",
        "object_link",
        "action_description",
        "get_change_message",
    )

    def has_add_permission(
        self,
        request: "HttpRequest",  # noqa: ARG002
    ) -> bool:
        return False

    def has_change_permission(
        self,
        request: "HttpRequest",  # noqa: ARG002
        obj: "LogEntry | None" = None,  # noqa: ARG002
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: "HttpRequest",  # noqa: ARG002
        obj: "LogEntry | None" = None,  # noqa: ARG002
    ) -> bool:
        return False

    def object_link(self, obj: "LogEntry") -> str:
        object_link = escape(obj.object_repr)
        content_type = obj.content_type

        if obj.action_flag != DELETION and content_type is not None:
            # Try returning an actual link instead of object repr string
            try:
                url = reverse(
                    f"admin:{content_type.app_label}_{content_type.model}_change",
                    args=[obj.object_id],
                )
                object_link = f'<a href="{url}">{object_link}</a>'
            except NoReverseMatch:
                pass
        return mark_safe(object_link)

    object_link.admin_order_field = "object_repr"
    object_link.short_description = _("object")

    def user_link(self, obj: "LogEntry") -> str:
        content_type = ContentType.objects.get_for_model(type(obj.user))
        user_link = escape(force_str(obj.user))
        try:
            # try returning an actual link instead of object repr string
            url = reverse(
                f"admin:{content_type.app_label}_{content_type.model}_change",
                args=[obj.user.pk],
            )
            user_link = f'<a href="{url}">{user_link}</a>'
        except NoReverseMatch:
            pass
        return mark_safe(user_link)

    user_link.admin_order_field = "user"
    user_link.short_description = _("user")

    def get_queryset(self, request: "HttpRequest") -> "models.QuerySet[LogEntry]":
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("content_type")

    def get_actions(self, request: "HttpRequest") -> dict[str, str]:
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def action_description(self, obj: "LogEntry") -> str:
        return action_names[obj.action_flag]

    action_description.short_description = _("action")
