from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django.contrib.auth import get_user_model
User = get_user_model()

# ---------- LoginForm ----------
class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email',
        'required': 'true'
    }))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password',
        'required': 'true'
    }))


# ---------- SignupForm ----------
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }), label='Password')

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }), label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        if password:
            errors = []
            if len(password) < 8:
                errors.append("at least 8 characters")
            if not re.search(r'[A-Z]', password):
                errors.append("at least one uppercase letter")
            if not re.search(r'[a-z]', password):
                errors.append("at least one lowercase letter")
            if not re.search(r'\d', password):
                errors.append("at least one number")
            if not re.search(r'[^\w\s]', password):
                errors.append("at least one special character (e.g., !@#$%)")

            if errors:
                raise ValidationError(f"Password must contain: {', '.join(errors)}.")

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if ' ' in username:
            raise ValidationError("Username cannot contain spaces.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# ---------- TransactionForm ----------
class TransactionForm(forms.Form):
    amount = forms.FloatField(label='Transaction Amount', min_value=0.01)
    # Add more fields if needed for prediction
    currency = forms.ChoiceField(choices=[
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('INR', 'INR'),
        ('GBP', 'GBP'),
    ])