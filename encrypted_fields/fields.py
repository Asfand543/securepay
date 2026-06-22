from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models
import base64

fernet = Fernet(settings.ENCRYPTION_KEY)

class EncryptedFieldMixin:
    def get_prep_value(self, value):
        if value is None:
            return None
        value = str(value).encode()
        return fernet.encrypt(value).decode()

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        try:
            return fernet.decrypt(value.encode()).decode()
        except InvalidToken:
            return None

    def to_python(self, value):
        if value is None:
            return None
        try:
            return fernet.decrypt(value.encode()).decode()
        except InvalidToken:
            return value

class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    pass

class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    pass

class EncryptedDateField(EncryptedFieldMixin, models.DateField):
    def to_python(self, value):
        val = super().to_python(value)
        return val
