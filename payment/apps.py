# payment_unique/apps.py
from django.apps import AppConfig

class PaymentUniqueConfig(AppConfig):
    name = 'payment'

# payment/apps.py
from django.apps import AppConfig

class PaymentConfig(AppConfig):
    name = 'payment'

    def ready(self):
        import payment.signals  # Import the signals to connect them
