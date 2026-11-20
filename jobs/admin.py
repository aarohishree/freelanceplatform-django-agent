from django.contrib import admin

from .models import Job, Proposal


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "budget", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "description", "client__username")
    list_select_related = ("client",)


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("job", "freelancer", "bid_amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("job__title", "freelancer__username")
    list_select_related = ("job", "freelancer")