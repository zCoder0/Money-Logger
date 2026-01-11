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

class TransactionForm(forms.ModelForm):
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
    
    class Meta:
        model = Transaction
        fields = [
            "transaction_type",
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
