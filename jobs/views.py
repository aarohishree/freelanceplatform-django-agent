from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Job, Proposal
from .permissions import IsClient, IsFreelancer, IsJobOwner
from .selectors import jobs_visible_to, proposals_visible_to
from .serializers import JobSerializer, ProposalSerializer


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "budget"]

    def get_permissions(self):
        if self.action == "create":
            classes = [IsAuthenticated, IsClient]
        elif self.action in ("update", "partial_update", "destroy", "close"):
            classes = [IsAuthenticated, IsClient, IsJobOwner]
        else:
            classes = [IsAuthenticated]
        return [cls() for cls in classes]

    def get_queryset(self):
        queryset = jobs_visible_to(self.request.user)
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def perform_destroy(self, instance):
        if instance.status != Job.Status.OPEN:
            raise ValidationError("Only open jobs can be deleted.")
        instance.delete()

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        job = self.get_object()
        if job.status != Job.Status.OPEN:
            raise ValidationError("Only open jobs can be closed.")
        job.status = Job.Status.CLOSED
        job.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(job).data)


class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "submit"):
            classes = [IsAuthenticated, IsFreelancer]
        elif self.action in ("accept", "reject"):
            classes = [IsAuthenticated, IsClient]
        else:
            classes = [IsAuthenticated]
        return [cls() for cls in classes]

    def get_queryset(self):
        return proposals_visible_to(self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.status != Proposal.Status.DRAFT:
            raise ValidationError("Only draft proposals can be edited.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.status != Proposal.Status.DRAFT:
            raise ValidationError("Only draft proposals can be deleted.")
        instance.delete()

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        proposal = self.get_object()
        if proposal.status != Proposal.Status.DRAFT:
            raise ValidationError("Only draft proposals can be submitted.")
        if proposal.job.status != Job.Status.OPEN:
            raise ValidationError("This job is no longer open.")
        proposal.status = Proposal.Status.SUBMITTED
        proposal.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        proposal = self.get_object()
        with transaction.atomic():
            job = Job.objects.select_for_update().get(pk=proposal.job_id)
            proposal.refresh_from_db()
            if proposal.status != Proposal.Status.SUBMITTED:
                raise ValidationError("Only submitted proposals can be accepted.")
            if job.status != Job.Status.OPEN:
                raise ValidationError("This job is no longer open.")
            proposal.status = Proposal.Status.ACCEPTED
            proposal.save(update_fields=["status", "updated_at"])
            job.status = Job.Status.IN_PROGRESS
            job.save(update_fields=["status", "updated_at"])
            job.proposals.filter(status=Proposal.Status.SUBMITTED).exclude(
                pk=proposal.pk
            ).update(status=Proposal.Status.REJECTED)
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        proposal = self.get_object()
        if proposal.status != Proposal.Status.SUBMITTED:
            raise ValidationError("Only submitted proposals can be rejected.")
        proposal.status = Proposal.Status.REJECTED
        proposal.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(proposal).data)