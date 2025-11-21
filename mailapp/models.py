# mailapp/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model with PGP key storage.
    """
    pgp_private_key = models.TextField(blank=True, null=True)
    pgp_public_key = models.TextField(blank=True, null=True)

    # Override default related_names to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username


class Email(models.Model):
    """
    Email model for storing messages locally.
    """
    sender = models.EmailField()
    recipients = models.CharField(max_length=500)  # comma-separated emails
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_encrypted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} from {self.sender}"
