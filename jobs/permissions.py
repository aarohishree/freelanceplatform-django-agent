from rest_framework.permissions import BasePermission

from accounts.models import User


class IsClient(BasePermission):
    message = "Only clients can do this."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.Role.CLIENT)


class IsFreelancer(BasePermission):
    message = "Only freelancers can do this."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.Role.FREELANCER)


class IsJobOwner(BasePermission):
    message = "You can only modify your own jobs."

    def has_object_permission(self, request, view, obj):
        return obj.client_id == request.user.id