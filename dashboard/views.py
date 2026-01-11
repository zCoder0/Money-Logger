from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, date
from ledger.models import Transaction

from django.template.loader import render_to_string
from django.http import JsonResponse

@login_required
def dashboard(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    page = request.GET.get("page", 1)

    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Filter dates safely
    from datetime import datetime
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            transactions = transactions.filter(date__gte=start_date_obj)
        except ValueError:
            pass
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            transactions = transactions.filter(date__lte=end_date_obj)
        except ValueError:
            pass

    paginator = Paginator(transactions, 10)
    transactions_page = paginator.get_page(page)

    total_income = transactions.filter(transaction_type="INCOME").aggregate(total=Sum("amount"))["total"] or 0
    total_expense = transactions.filter(transaction_type="EXPENSE").aggregate(total=Sum("amount"))["total"] or 0
    balance = total_income - total_expense

    context = {
        "transactions": transactions_page,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "start_date": start_date,
        "end_date": end_date,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return only the table and pagination part
        html = render_to_string('dashboard/_transactions_table.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, "dashboard/dashboard.html", context)



@login_required
def analytics(request):
    from datetime import datetime, timedelta
    from django.db.models import Q
    from calendar import month_name
    
    # Get current month/year or from request
    current_date = datetime.now()
    selected_month = int(request.GET.get('month', current_date.month))
    selected_year = int(request.GET.get('year', current_date.year))
    
    transactions = Transaction.objects.filter(user=request.user)
    
    # Filter by selected month/year
    month_transactions = transactions.filter(
        date__year=selected_year,
        date__month=selected_month
    )
    
    # Overall totals
    total_income = transactions.filter(transaction_type="INCOME").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = transactions.filter(transaction_type="EXPENSE").aggregate(Sum("amount"))["amount__sum"] or 0
    balance = total_income - total_expense
    total_transactions = transactions.count()
    
    # Current month totals
    month_income = month_transactions.filter(transaction_type="INCOME").aggregate(Sum("amount"))["amount__sum"] or 0
    month_expense = month_transactions.filter(transaction_type="EXPENSE").aggregate(Sum("amount"))["amount__sum"] or 0
    month_balance = month_income - month_expense
    month_transaction_count = month_transactions.count()
    
    # Category-wise expense for current month
    category_expense = month_transactions.filter(transaction_type="EXPENSE")\
        .values("category")\
        .annotate(total=Sum("amount"))\
        .order_by("-total")
    
    # Category-wise income for current month
    category_income = month_transactions.filter(transaction_type="INCOME")\
        .values("category")\
        .annotate(total=Sum("amount"))\
        .order_by("-total")
    
    # Daily data for current month - simplified approach
    import calendar
    days_in_month = calendar.monthrange(selected_year, selected_month)[1]
    daily_labels = [str(i) for i in range(1, days_in_month + 1)]
    daily_income = [0] * days_in_month
    daily_expense = [0] * days_in_month
    
    # Get daily transactions and aggregate manually
    daily_transactions = month_transactions.values('date', 'transaction_type', 'amount')
    for transaction in daily_transactions:
        day_index = transaction['date'].day - 1
        if transaction['transaction_type'] == 'INCOME':
            daily_income[day_index] += float(transaction['amount'])
        else:
            daily_expense[day_index] += float(transaction['amount'])
    
    # Monthly trend for the year
    yearly_monthly = transactions.filter(date__year=selected_year)\
        .annotate(month=TruncMonth("date"))\
        .values("month", "transaction_type")\
        .annotate(total=Sum("amount"))\
        .order_by("month")
    
    # Prepare yearly monthly chart data
    month_labels = [month_name[i] for i in range(1, 13)]
    yearly_income = [0] * 12
    yearly_expense = [0] * 12
    
    for item in yearly_monthly:
        month_index = item["month"].month - 1
        if item["transaction_type"] == "INCOME":
            yearly_income[month_index] = float(item["total"])
        else:
            yearly_expense[month_index] = float(item["total"])
    
    # Navigation dates
    current_month_date = datetime(selected_year, selected_month, 1)
    prev_month = current_month_date - timedelta(days=1)
    next_month_date = current_month_date.replace(day=28) + timedelta(days=4)
    next_month = next_month_date - timedelta(days=next_month_date.day-1)
    
    context = {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "total_transactions": total_transactions,
        "month_income": month_income,
        "month_expense": month_expense,
        "month_balance": month_balance,
        "month_transaction_count": month_transaction_count,
        "category_expense": category_expense,
        "category_income": category_income,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "month_name": month_name[selected_month],
        "prev_month": prev_month.month,
        "prev_year": prev_month.year,
        "next_month": next_month.month,
        "next_year": next_month.year,
        "daily_labels": daily_labels,
        "daily_income": daily_income,
        "daily_expense": daily_expense,
        "month_labels": month_labels,
        "yearly_income": yearly_income,
        "yearly_expense": yearly_expense,
    }
    
    return render(request, "dashboard/analytics.html", context)
