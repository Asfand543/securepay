# your_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # Include payment and secure_payment app URLs
    path('payment/', include('payment.urls', namespace='payment')),
    path('secure_payment/', include('secure_payment.urls', namespace='secure_payment')),

    # Optionally, you can include other app URLs or custom views
    # path('some_other_app/', include('some_other_app.urls', namespace='some_other_app')),
]

# Custom error handlers can be added here (if required)
handler404 = 'payment.views.page_not_found_view'
handler500 = 'payment.views.server_error_view'
