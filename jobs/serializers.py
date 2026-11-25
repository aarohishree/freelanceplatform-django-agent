from rest_framework import serializers

from .models import Job, Proposal


class JobSerializer(serializers.ModelSerializer):
    client = serializers.ReadOnlyField(source="client.username")

    class Meta:
        model = Job
        fields = [
            "id", "client", "title", "description",
            "budget", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_budget(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget must be greater than zero.")
        return value


class ProposalSerializer(serializers.ModelSerializer):
    freelancer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    freelancer_name = serializers.ReadOnlyField(source="freelancer.username")

    class Meta:
        model = Proposal
        fields = [
            "id", "job", "freelancer", "freelancer_name",
            "cover_letter", "bid_amount", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate(self, attrs):
        if self.instance and "job" in attrs and attrs["job"] != self.instance.job:
            raise serializers.ValidationError(
                {"job": "You cannot move a proposal to a different job."}
            )
        return attrs

    def validate_bid_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Bid must be greater than zero.")
        return value

    def validate_job(self, job):
        if job.status != Job.Status.OPEN:
            raise serializers.ValidationError("This job is not accepting proposals.")
        return job