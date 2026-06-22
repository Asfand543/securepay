# secure_payment/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from payment import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('payment/', include('payment.urls', namespace='payment')),
    path('fraud_detection/', views.fraud_detection_view, name='fraud_detection'),
    path('analytics/', views.analytics_view, name='analytics_view'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
