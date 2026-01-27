from django import forms
from .models import Transaction

CATEGORY_CHOICES = [
    ('Food', 'Food'),
    ('Snacks', 'Snacks'),
    ('Salary', 'Salary'),
    ('Family', 'Family'),
    ('Friend', 'Friend'),
    ('Rent', 'Rent'),
    ('Travels', 'Travels'),
    ('Home Things', 'Home Things'),
    ("Projects","Projects"),
    ("Purchasing","Purchasing"),
    ('Others', 'Others'),
]

MONEY_TYPE_CHOICES = [
    ('HAND CASH', 'Hand Cash'),
    ('UPI CASH', 'UPI Cash'),
]

class TransactionForm(forms.ModelForm):
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
    money_type = forms.ChoiceField(choices=MONEY_TYPE_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
    
    class Meta:
        model = Transaction
        fields = [
            "transaction_type",
            "money_type",
            "amount",
            "category",
            "description",
            "date",
        ]

        widgets = {
            "transaction_type": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

class SwitchForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "switch_direction", "description", "date"]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Enter amount"}),
            "switch_direction": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Optional note (e.g., ATM withdrawal, bank deposit)"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }
