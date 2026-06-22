# payment/utils.py

import requests
from django.conf import settings

def verify_recaptcha(request):
    secret_key = settings.RECAPTCHA_SECRET_KEY
    response = request.POST.get('g-recaptcha-response')
    data = {
        'secret': secret_key,
        'response': response
    }
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    verification_response = requests.post(verify_url, data=data)
    result = verification_response.json()
    return result.get('success', False)
