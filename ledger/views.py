from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .forms import TransactionForm, SwitchForm
from .models import Transaction

@login_required
def add_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            
            # Validate sufficient balance for expenses
            if transaction.transaction_type == "EXPENSE":
                all_transactions = Transaction.objects.filter(user=request.user)
                
                if transaction.money_type == "UPI CASH":
                    upi_income = all_transactions.filter(transaction_type="INCOME", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
                    upi_expense = all_transactions.filter(transaction_type="EXPENSE", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
                    upi_from_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
                    upi_to_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
                    upi_balance = upi_income - upi_expense + upi_from_switch - upi_to_switch
                    
                    if transaction.amount > upi_balance:
                        messages.error(request, f"⚠️ Insufficient UPI Cash balance! Available: ₹{upi_balance:.2f}, Required: ₹{transaction.amount}")
                        return render(request, "ledger/add_transaction.html", {"form": form})
                
                elif transaction.money_type == "HAND CASH":
                    hand_income = all_transactions.filter(transaction_type="INCOME", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
                    hand_expense = all_transactions.filter(transaction_type="EXPENSE", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
                    hand_from_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
                    hand_to_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
                    hand_balance = hand_income - hand_expense + hand_from_switch - hand_to_switch
                    
                    if transaction.amount > hand_balance:
                        messages.error(request, f"⚠️ Insufficient Hand Cash balance! Available: ₹{hand_balance:.2f}, Required: ₹{transaction.amount}")
                        return render(request, "ledger/add_transaction.html", {"form": form})
            
            transaction.save()
            return redirect("dashboard")
    else:
        form = TransactionForm()

    return render(request, "ledger/add_transaction.html", {"form": form})

@login_required
def switch_money(request):
    if request.method == "POST":
        form = SwitchForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.transaction_type = "SWITCH"
            transaction.category = "Money Transfer"
            
            # Validate sufficient balance for switch
            all_transactions = Transaction.objects.filter(user=request.user)
            
            if transaction.switch_direction == "UPI_TO_HAND":
                upi_income = all_transactions.filter(transaction_type="INCOME", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
                upi_expense = all_transactions.filter(transaction_type="EXPENSE", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
                upi_from_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
                upi_to_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
                upi_balance = upi_income - upi_expense + upi_from_switch - upi_to_switch
                
                if transaction.amount > upi_balance:
                    messages.error(request, f"⚠️ Insufficient UPI Cash balance! Available: ₹{upi_balance:.2f}, Required: ₹{transaction.amount}")
                    return render(request, "ledger/switch_money.html", {"form": form})
            
            elif transaction.switch_direction == "HAND_TO_UPI":
                hand_income = all_transactions.filter(transaction_type="INCOME", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
                hand_expense = all_transactions.filter(transaction_type="EXPENSE", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
                hand_from_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
                hand_to_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
                hand_balance = hand_income - hand_expense + hand_from_switch - hand_to_switch
                
                if transaction.amount > hand_balance:
                    messages.error(request, f"⚠️ Insufficient Hand Cash balance! Available: ₹{hand_balance:.2f}, Required: ₹{transaction.amount}")
                    return render(request, "ledger/switch_money.html", {"form": form})
            
            if not transaction.description:
                transaction.description = f"Switched from {dict(transaction.SWITCH_DIRECTION)[transaction.switch_direction]}"
            transaction.save()
            return redirect("dashboard")
    else:
        form = SwitchForm()
    
    return render(request, "ledger/switch_money.html", {"form": form})
