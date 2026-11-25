from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Job, Proposal
from jobs.permissions import IsFreelancer
from jobs.selectors import jobs_visible_to
from jobs.serializers import ProposalSerializer

from .models import AgentRun
from .services import get_llm_client, run_proposal_drafter


class DraftProposalView(APIView):
    permission_classes = [IsAuthenticated, IsFreelancer]

    def post(self, request, job_id):
        job = get_object_or_404(jobs_visible_to(request.user), pk=job_id)

        # Cheap checks first, so we don't pay for an AI call that was going to be rejected.
        if job.status != Job.Status.OPEN:
            raise ValidationError("This job is not accepting proposals.")
        if Proposal.objects.filter(job=job, freelancer=request.user).exists():
            raise ValidationError("You already have a proposal for this job.")

        try:
            client = get_llm_client()
        except RuntimeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        run = run_proposal_drafter(request.user, job, client)
        if run.status != AgentRun.Status.DONE:
            return Response(
                {"run_id": run.id, "error": run.error}, status=status.HTTP_502_BAD_GATEWAY
            )

        # The agent only ever creates a DRAFT. The freelancer reviews it and submits it.
        proposal = Proposal.objects.create(
            job=job,
            freelancer=request.user,
            cover_letter=run.output["cover_letter"],
            bid_amount=run.output["bid_amount"],
            status=Proposal.Status.DRAFT,
        )
        data = ProposalSerializer(proposal, context={"request": request}).data
        return Response(
            {
                "run_id": run.id,
                "steps": [step["tool"] for step in run.steps],
                "proposal": data,
            },
            status=status.HTTP_201_CREATED,
        )