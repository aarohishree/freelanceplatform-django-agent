from django.urls import path

from .views import DraftProposalView

urlpatterns = [
    path("jobs/<int:job_id>/draft-proposal/", DraftProposalView.as_view()),
]