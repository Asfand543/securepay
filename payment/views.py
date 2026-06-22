import uuid
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.conf import settings
from .forms import LoginForm, SignupForm, TransactionForm
from .utils import verify_recaptcha
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import get_user_model
from .models import Transaction, PredictionLog
from .predict import predict_transaction  # Correct import
from .models import Transaction, PredictionLog
import os
import joblib

User = get_user_model()
# ===================
# HOMEPAGE
# ===================
def home_view(request):
    return render(request, 'payment/homepage.html')

def index(request):
    return render(request, 'index.html')

# ===================
# SIGNUP
# ===================
def signup_view(request):
    form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')

            if password != confirm_password:
                form.add_error('confirm_password', 'Passwords do not match!')
            else:
                form.save()
                return redirect('payment:step1')
    return render(request, 'payment/signup.html', {
        'form': form,
        'site_key': settings.RECAPTCHA_SITE_KEY
    })

# ===================
# LOGIN
# ===================
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.conf import settings
from .models import CustomUser  # Import your custom user model

def login_view(request):
    context = {'site_key': settings.RECAPTCHA_SITE_KEY}

    if request.method == 'POST':
        # Verify reCAPTCHA
        if not verify_recaptcha(request):
            context['error'] = 'Invalid CAPTCHA. Please try again.'
            return render(request, 'payment/login.html', context)

        # Get credentials from the form
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Try to fetch the user with the given email using CustomUser model
        try:
            user = CustomUser.objects.get(email=email)  # Fetch the user using the custom email field
        except CustomUser.DoesNotExist:
            context['error'] = 'User does not exist.'
            return render(request, 'payment/login.html', context)

        # Authenticate the user
        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            login(request, user)  # Log the user in
            return redirect('payment:dashboard')  # Redirect to the dashboard after login
        else:
            context['error'] = 'Invalid credentials.'
            return render(request, 'payment/login.html', context)

    return render(request, 'payment/login.html', context)

# ===================
# TERMS
# ===================
def terms_page(request):
    return render(request, 'payment/terms.html')

# views.py
  # Assuming you have a Transaction model for storing transactions

# views.py
  # Assuming you have a Transaction model for storing transactions


from django.db.models import Count
from django.db.models.functions import TruncWeek
from django.utils import timezone
from datetime import timedelta
from .models import Transaction
from django.shortcuts import render

def analytics_view(request):
    # Example: fetch the total number of transactions
    total_transactions = Transaction.objects.count()
    successful_transactions = Transaction.objects.filter(status='Success').count()
    failed_transactions = Transaction.objects.filter(status='Failed').count()

    # Calculate transactions for the last 4 weeks (for the chart)
    weeks_ago = timezone.now() - timedelta(weeks=4)
    
    # Group transactions by week and status (successful or failed)
    weekly_successful = (
        Transaction.objects.filter(status='Success', timestamp__gte=weeks_ago)
        .annotate(week=TruncWeek('timestamp'))
        .values('week')
        .annotate(count=Count('id'))
        .order_by('week')
    )
    
    weekly_failed = (
        Transaction.objects.filter(status='Failed', timestamp__gte=weeks_ago)
        .annotate(week=TruncWeek('timestamp'))
        .values('week')
        .annotate(count=Count('id'))
        .order_by('week')
    )

    # Prepare data for the chart (filling in missing weeks if no data is present for a week)
    week_labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    successful_transactions_data = [0, 0, 0, 0]
    failed_transactions_data = [0, 0, 0, 0]
    
    # Adjust data based on the queried results
    for i, week in enumerate(weekly_successful):
        # The `week` field will be a datetime object, so you may need to convert it into a week index (Week 1, Week 2, etc.)
        # You can match it to the corresponding index of `week_labels`
        week_index = (timezone.now() - week['week']).days // 7
        if week_index < 4:  # Make sure we don't go out of bounds
            successful_transactions_data[week_index] = week['count']

    for i, week in enumerate(weekly_failed):
        # Similar handling for failed transactions
        week_index = (timezone.now() - week['week']).days // 7
        if week_index < 4:  # Make sure we don't go out of bounds
            failed_transactions_data[week_index] = week['count']

    # Pass all data to the context
    context = {
        'total_transactions': total_transactions,
        'successful_transactions': successful_transactions,
        'failed_transactions': failed_transactions,
        'successful_transactions_data': successful_transactions_data,
        'failed_transactions_data': failed_transactions_data,
        'week_labels': week_labels,
    }

    return render(request, 'payment/analytics.html', context)


# ===================
# MULTI-STEP USER DETAILS
# ===================
def step1_view(request):
    if request.method == 'POST':
        request.session['phone_number'] = request.POST.get('phone_number')
        request.session['cnic'] = request.POST.get('cnic')
        request.session['address'] = request.POST.get('address')
        request.session['city'] = request.POST.get('city')
        request.session['postal_code'] = request.POST.get('postal_code')
        request.session['dob'] = request.POST.get('dob')
        request.session['cnic_issue_date'] = request.POST.get('cnic_issue_date')
        request.session['cnic_expiry_date'] = request.POST.get('cnic_expiry_date')
        return redirect('payment:step2')
    return render(request, 'payment/step1.html')

def step2_view(request):
    if request.method == 'POST' and request.FILES:
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        cnic_front = request.FILES.get('cnic_front')
        cnic_back = request.FILES.get('cnic_back')
        personal_picture = request.FILES.get('personal_picture')

        if not all([cnic_front, cnic_back, personal_picture]):
            return render(request, 'payment/step2.html', {'error': 'All files required'})

        request.session['cnic_front_url'] = fs.url(fs.save(f'cnic_front/{cnic_front.name}', cnic_front))
        request.session['cnic_back_url'] = fs.url(fs.save(f'cnic_back/{cnic_back.name}', cnic_back))
        request.session['personal_picture_url'] = fs.url(fs.save(f'personal_picture/{personal_picture.name}', personal_picture))
        return redirect('payment:step3')

    return render(request, 'payment/step2.html')

def step3_view(request):
    if request.method == 'POST':
        return redirect('payment:complete')

    context = {
        'username': request.session.get('username'),
        'email': request.session.get('email'),
        'cnic': request.session.get('cnic'),
        'phone_number': request.session.get('phone_number'),
        'address': request.session.get('address'),
        'city': request.session.get('city'),
        'postal_code': request.session.get('postal_code'),
        'dob': request.session.get('dob'),
        'cnic_expiry_date': request.session.get('cnic_expiry_date'),
        'cnic_front_url': request.session.get('cnic_front_url'),
        'cnic_back_url': request.session.get('cnic_back_url'),
        'personal_picture_url': request.session.get('personal_picture_url'),
    }
    return render(request, 'payment/step3.html', context)

@csrf_protect
def complete_view(request):
    for key in ['phone_number', 'cnic', 'address', 'city', 'postal_code', 'dob',
                'cnic_issue_date', 'cnic_expiry_date', 'cnic_front_url',
                'cnic_back_url', 'personal_picture_url']:
        request.session.pop(key, None)
    return render(request, 'payment/complete.html')

# ===================
# TRANSACTION PREDICTION
# ===================

# views.py

@login_required
def predict_transaction_view(request):
    if request.method == 'POST':
        try:
            input_data = {
                'step': int(request.POST.get('step', 0)),
                'amount': float(request.POST.get('amount', 0)),
                'oldbalanceOrg': float(request.POST.get('oldbalanceOrg', 0)),
                'newbalanceOrig': float(request.POST.get('newbalanceOrig', 0)),
                'oldbalanceDest': float(request.POST.get('oldbalanceDest', 0)),
                'newbalanceDest': float(request.POST.get('newbalanceDest', 0)),
                'isFlaggedFraud': int(request.POST.get('isFlaggedFraud', 0)),
                'CASH_OUT': int(request.POST.get('CASH_OUT', 0)),
                'DEBIT': int(request.POST.get('DEBIT', 0)),
                'PAYMENT': int(request.POST.get('PAYMENT', 0)),
                'TRANSFER': int(request.POST.get('TRANSFER', 0)),
            }

            result = predict_transaction(input_data)

            if 'error' in result:
                raise ValueError(result['error'])

            # Log the prediction
            PredictionLog.objects.create(
                user=request.user,
                input_data=input_data,
                prediction=result['prediction'],
                fraud_probability=result['fraud_probability']
            )

            # Save transaction info
            Transaction.objects.create(
                sender=request.user,
                receiver=request.user,  # You can update this logic later
                amount=input_data['amount'],
                status='Completed',
                is_fraud=result['prediction'] == 'Fraudulent',
                fraud_score=result['fraud_probability'],
                reference_id="TXN-" + str(uuid.uuid4())[:12]
            )

            return render(request, 'result.html', {
                'prediction': result['prediction'],
                'probability': round(result['fraud_probability'] * 100, 2),
                'amount': input_data['amount'],
                'currency': "PKR"  # Hardcoded, change if needed
            })

        except Exception as e:
            return render(request, 'result.html', {
                'error': f"Prediction failed: {str(e)}"
            })

    return render(request, 'payment/predict.html')

# payment/views.py

from .forms import TransactionForm

def fraud_detection_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction_data = form.cleaned_data
            prediction = make_prediction(transaction_data)
            is_fraud = prediction == 'fraud'
            
            return render(request, 'result.html', {
                'prediction': prediction,
                'is_fraud': is_fraud
            })
    else:
        form = TransactionForm()
    
    return render(request, 'fraud_detection.html', {'form': form})

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

@login_required
def transaction_view(request):
    # ✅ Fetch transactions where user is sender or receiver
    transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')

    # Assign CSS classes for status
    for tx in transactions:
        if tx.status == 'Completed':
            tx.status_class = 'completed'
        elif tx.status == 'Pending':
            tx.status_class = 'pending'
        else:
            tx.status_class = 'failed'

    message = None
    message_type = None

    if request.method == 'POST':
        receiver_username = request.POST.get('receiver_username')
        amount = request.POST.get('amount')

        try:
            receiver = User.objects.get(username=receiver_username)

            Transaction.objects.create(
                sender=request.user,
                receiver=receiver,
                amount=amount,
                status="Completed"
            )

            # Optional: email
            send_mail(
                subject='SecurePay Transaction Notification',
                message=f'You sent ${amount} to {receiver.username}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True
            )

            message = 'Transaction successful!'
            message_type = 'success'

        except User.DoesNotExist:
            message = 'Receiver not found.'
            message_type = 'error'
        except Exception as e:
            message = f'Error: {str(e)}'
            message_type = 'error'

    context = {
        'transactions': transactions,
        'message': message,
        'message_type': message_type,
    }

    return render(request, 'payment/transactions.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from .models import Transaction  # Ensure this model exists and is imported
from django.utils import timezone

@login_required
def send_transaction(request):
    if request.method == 'POST':
        receiver = request.POST.get('receiver_username')
        amount = request.POST.get('amount')

        # Optionally: validate receiver
        if not receiver or not amount:
            messages.error(request, "All fields are required.")
            return redirect('accounts')

        # Save the transaction to the database
        tx = Transaction.objects.create(
            user=request.user,
            person_name=receiver,
            type="Transfer",
            amount=amount,
            date=timezone.now(),
            status="pending"  # Set to completed/failed based on logic
        )

        # Send email to sender
        send_mail(
            subject='Transaction Sent - SecurePay AI',
            message=f'You successfully sent ${amount} to {receiver}.',
            from_email='noreply@securepay.ai',
            recipient_list=[request.user.email],
            fail_silently=False,
        )

        messages.success(request, f'Transaction to {receiver} sent. Email confirmation sent.')
        return redirect('accounts')  # Make sure 'accounts' is a valid named route

    return redirect('accounts')


# payment/views.py

from django.shortcuts import render
# ===================
# DASHBOARD
# ===================
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    # Example of dummy data; replace with actual database queries
    stat_cards = [
        {'name': 'Card Transfers', 'amount': 1500},
        {'name': 'Bank Transfers', 'amount': 2200},
        {'name': 'Same Bank', 'amount': 2500},
        {'name': 'Via UPI', 'amount': 1200},
    ]

    monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
    monthly_expenses = [3000, 4000, 3200, 5000, 6100, 2800, 3600, 4200]
    monthly_income = [5000, 5500, 4800, 6200, 7000, 5100, 5300, 6000]

    # Sample data for recent activity, balance, etc.
    recent_activity = [
        {'name': 'Water Bill', 'amount': 85},
        {'name': 'Internet', 'amount': 95},
        {'name': 'Electricity', 'amount': 105},
        {'name': 'Rent', 'amount': 225},
    ]
    
    transactions = [
        {'person_name': 'Alex', 'type': 'Car Insurance', 'date': '12/02/2023 09:25 AM', 'amount': 280, 'status': 'Completed', 'status_class': 'text-green-400', 'person_avatar': 'https://i.pravatar.cc/30'},
        {'person_name': 'Sam', 'type': 'Library Fee', 'date': '10/02/2023 10:45 AM', 'amount': 30, 'status': 'Pending', 'status_class': 'text-yellow-400', 'person_avatar': 'https://i.pravatar.cc/30?img=2'},
        {'person_name': 'Nina', 'type': 'Loan EMI', 'date': '05/02/2023 11:00 AM', 'amount': 1500, 'status': 'Failed', 'status_class': 'text-red-400', 'person_avatar': 'https://i.pravatar.cc/30?img=3'},
    ]

    user_balance = 9580
    upcoming_payments = 560

    return render(request, 'payment/dashboard.html', {
        'stat_cards': stat_cards,
        'monthly_labels': monthly_labels,
        'monthly_expenses': monthly_expenses,
        'monthly_income': monthly_income,
        'recent_activity': recent_activity,
        'transactions': transactions,
        'user_balance': user_balance,
        'upcoming_payments': upcoming_payments,
    })

def accounts_view(request):
    # Your logic for the accounts page
    return render(request, 'payment/accounts.html')

def invoices_view(request):
    return render(request, 'payment/invoices.html')

def reports_view(request):
    return render(request, 'payment/reports.html')

def settings_view(request):
    return render(request, 'payment/settings.html')

# ===================
# ERROR HANDLING
# ===================
def page_not_found_view(request, exception):
    return render(request, 'payment/404.html', status=404)

def server_error_view(request):
    return render(request, 'payment/500.html', status=500)

from django.http import HttpResponseForbidden

def custom_csrf_failure(request, reason=""):
    return HttpResponseForbidden("CSRF token missing or incorrect")
