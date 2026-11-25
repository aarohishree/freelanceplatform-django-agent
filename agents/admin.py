from django.contrib import admin

from .models import AgentRun


@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display = ("id", "agent", "user", "status", "input_tokens", "output_tokens", "created_at")
    list_filter = ("status",)
    list_select_related = ("user",)
    readonly_fields = [f.name for f in AgentRun._meta.fields]

    def has_add_permission(self, request):
        return False