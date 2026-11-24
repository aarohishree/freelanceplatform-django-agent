from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Job, Proposal
from .serializers import JobSerializer, ProposalSerializer


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "budget"]

    def get_queryset(self):
        queryset = Job.objects.select_related("client")
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer

    def get_queryset(self):
        return Proposal.objects.select_related("job", "freelancer")