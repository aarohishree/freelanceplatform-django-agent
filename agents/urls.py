from django.urls import path

from .views import AgentChatView, DraftProposalView

urlpatterns = [
    path("agent/chat/", AgentChatView.as_view()),
    path("jobs/<int:job_id>/draft-proposal/", DraftProposalView.as_view()),
]