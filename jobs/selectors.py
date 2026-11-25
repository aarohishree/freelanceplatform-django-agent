from accounts.models import User

from .models import Job, Proposal


def jobs_visible_to(user):
    # A marketplace: every logged-in user can browse jobs.
    return Job.objects.select_related("client")


def proposals_visible_to(user):
    qs = Proposal.objects.select_related("job", "freelancer")
    role = getattr(user, "role", None)
    if role == User.Role.FREELANCER:
        return qs.filter(freelancer=user)
    if role == User.Role.CLIENT:
        return qs.filter(job__client=user).exclude(status=Proposal.Status.DRAFT)
    return qs.none()