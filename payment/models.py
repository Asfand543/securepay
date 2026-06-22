from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from fernet_fields import EncryptedCharField, EncryptedTextField, EncryptedDateField
from decimal import Decimal, InvalidOperation
import logging

STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
    ('Failed', 'Failed'),
)

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    balance = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)

    phone_number = EncryptedCharField(max_length=128, blank=True, null=True)
    cnic = EncryptedCharField(max_length=128, blank=True, null=True)
    address = EncryptedTextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    cnic_issue_date = EncryptedDateField(blank=True, null=True)
    cnic_expiry_date = EncryptedDateField(blank=True, null=True)

    def __str__(self):
        return self.username

    def clean(self):
        """
        Ensure that the balance is a valid Decimal value and handle invalid input.
        """
        # Ensure balance is a valid Decimal value
        try:
            # Convert to Decimal, in case it's a string or other invalid type
            self.balance = Decimal(self.balance)
        except (InvalidOperation, ValueError) as e:
            # Log the error for debugging
            logger = logging.getLogger(__name__)
            logger.error(f"Invalid balance value for {self.username}: {e}")
            
            # Set to a default value if invalid
            self.balance = Decimal('0.00')

        super().clean()


class Transaction(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    fraud_score = models.FloatField(default=0.0)
    is_fraud = models.BooleanField(default=False)  # Removed duplicate field
    reference_id = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} | ₹{self.amount} [{self.status}]"

    def clean(self):
        """
        Ensure that the amount is a valid Decimal value and handle invalid input.
        """
        try:
            # Attempt to convert the amount to a valid Decimal
            self.amount = Decimal(self.amount)
        except (InvalidOperation, ValueError) as e:
            # Log the error for debugging
            logger = logging.getLogger(__name__)
            logger.error(f"Invalid amount '{self.amount}' in transaction ID {self.id}: {e}")
            
            # Set amount to a default value if invalid
            self.amount = Decimal('0.00')

        super().clean()


class PredictionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    input_data = models.JSONField()
    prediction = models.CharField(max_length=20)
    fraud_probability = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.prediction} ({self.fraud_probability})"
