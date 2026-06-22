# payment/urls.py

from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('terms/', views.terms_page, name='terms_page'),
    path('step1/', views.step1_view, name='step1'),
    path('step2/', views.step2_view, name='step2'),
    path('step3/', views.step3_view, name='step3'),
    path('complete/', views.complete_view, name='complete'),
    path('login/', views.login_view, name='login'),  # Ensure this is here
    path('dashboard', views.dashboard_view, name='dashboard'),
    path('accounts/', views.accounts_view, name='accounts'),
    path('transactions/', views.transaction_view, name='transactions'),
    path('send_transaction/', views.send_transaction, name='send_transaction'), # new function
    path('invoices/', views.invoices_view, name='invoices'),
    path('settings/', views.settings_view, name='settings'),
    path('reports/', views.reports_view, name='reports'),
    path('analytics/', views.analytics_view, name='analytics'), 
      # Transaction page URL
    # other URLs...
    path('predict/', views.predict_transaction_view, name='predict_transaction_view'),
]
