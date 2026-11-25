from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    skills = models.CharField(max_length=300, blank=True)
    bio = models.TextField(blank=True)
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        FREELANCER = "freelancer", "Freelancer"

    role = models.CharField(max_length=20, choices=Role.choices)

    REQUIRED_FIELDS = ["role"]