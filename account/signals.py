import secrets

from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import AbstractUser
from .tasks import send_activation_mail


@receiver(pre_save, sender=AbstractUser)
def create_activation_code_signal(sender, instance, **kwargs):
    if not instance.pk:
        code = secrets.token_urlsafe(6)
        instance.activation_code = code
        send_activation_mail(instance.email, code)

