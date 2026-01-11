from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'category', 'description', 'date', 'created_at']
    list_filter = ['transaction_type', 'category', 'date', 'created_at']
    search_fields = ['description', 'category']
    date_hierarchy = 'date'
    ordering = ['-date']
