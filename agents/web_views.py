from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.models import User
from jobs.models import Job, Proposal


@login_required
def chat_page(request):
    if request.user.role != User.Role.FREELANCER:
        return render(request, "agents/chat.html", {"not_freelancer": True})

    already_proposed = Proposal.objects.filter(freelancer=request.user).values_list(
        "job_id", flat=True
    )
    jobs = Job.objects.filter(status=Job.Status.OPEN).exclude(id__in=already_proposed)
    return render(request, "agents/chat.html", {"jobs": jobs})