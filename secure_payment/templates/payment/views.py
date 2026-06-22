# secure_payment/views.py

from django.shortcuts import render

# Example view
def signup_view(request):
    return render(request, 'signup.html')

def login_view(request):
    return render(request, 'login.html')
