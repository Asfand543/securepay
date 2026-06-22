from django.contrib import admin
from .models import Transaction, CustomUser, PredictionLog
from django.contrib.auth.admin import UserAdmin

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'amount', 'is_fraud', 'status', 'timestamp')
    list_filter = ('status', 'is_fraud', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'reference_id')
    ordering = ('-timestamp',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'balance', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'role')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {'fields': ('role', 'balance')}),
    )

@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'prediction', 'fraud_probability', 'created_at')
    list_filter = ('prediction', 'created_at')
    search_fields = ('user__username', 'prediction')
    ordering = ('-created_at',)
