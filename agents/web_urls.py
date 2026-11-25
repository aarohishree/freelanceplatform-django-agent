from django.urls import path
from django.views.generic import RedirectView

from .web_views import chat_page

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="chat")),
    path("chat/", chat_page, name="chat"),
]