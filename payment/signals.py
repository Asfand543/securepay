# payment/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction
from .services import check_transaction

@receiver(post_save, sender=Transaction)
def evaluate_transaction(sender, instance, created, **kwargs):
    if created:
        instance.is_fraud = check_transaction(instance)
        instance.save()
    
# payment/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        # Send email upon user signup
        send_mail(
            'Welcome to SecurePay',
            f'Hello {instance.username},\n\nThank you for registering with SecurePay.',
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )
