from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, date
import calendar
from ledger.models import Transaction

from django.template.loader import render_to_string
from django.http import JsonResponse

@login_required
def dashboard(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    category = request.GET.get("category")
    transaction_type = request.GET.get("transaction_type")
    money_type = request.GET.get("money_type")
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
    
    # Filter by category
    if category:
        transactions = transactions.filter(category__icontains=category)
    
    # Filter by transaction type
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Filter by money type
    if money_type:
        transactions = transactions.filter(money_type=money_type)

    paginator = Paginator(transactions, 10)
    transactions_page = paginator.get_page(page)

    # Exclude SWITCH transactions from income/expense totals
    total_income = transactions.filter(transaction_type="INCOME").aggregate(total=Sum("amount"))["total"] or 0
    total_expense = transactions.filter(transaction_type="EXPENSE").aggregate(total=Sum("amount"))["total"] or 0
    balance = total_income - total_expense
    
    # Calculate balance by money type - FIXED LOGIC (excluding SWITCH)
    all_transactions = Transaction.objects.filter(user=request.user)
    
    # UPI Cash balance
    upi_income = all_transactions.filter(transaction_type="INCOME", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
    upi_expense = all_transactions.filter(transaction_type="EXPENSE", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
    upi_from_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
    upi_to_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
    upi_balance = upi_income - upi_expense + upi_from_switch - upi_to_switch
    
    # Hand Cash balance
    hand_income = all_transactions.filter(transaction_type="INCOME", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
    hand_expense = all_transactions.filter(transaction_type="EXPENSE", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
    hand_from_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
    hand_to_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
    hand_balance = hand_income - hand_expense + hand_from_switch - hand_to_switch
    
    # Survival calculations for warning
    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = max(1, today.day)
    days_left = days_in_month - today.day
    
    month_transactions = all_transactions.filter(date__year=today.year, date__month=today.month)
    expense_mtd = month_transactions.filter(transaction_type="EXPENSE").aggregate(Sum("amount"))["amount__sum"] or 0
    avg_daily_spend = float(expense_mtd) / days_passed if days_passed > 0 else 0
    projected_remaining_spend = avg_daily_spend * days_left
    available_funds = float(upi_balance) + float(hand_balance)
    projected_end_balance = available_funds - projected_remaining_spend
    survive = projected_end_balance >= 0
    
    # Today's spending
    today_expense = month_transactions.filter(transaction_type="EXPENSE", date=today).aggregate(Sum("amount"))["amount__sum"] or 0
    today_expense = float(today_expense)
    
    # Health score for warning
    health_score = 100
    if expense_mtd > total_income:
        health_score -= 20
    if projected_end_balance < 0:
        health_score -= 30
    if avg_daily_spend > 0 and today_expense > avg_daily_spend * 1.5:
        health_score -= 15
    
    # Days until broke
    days_until_broke = None
    if not survive and avg_daily_spend > 0:
        days_until_broke = int(available_funds / avg_daily_spend) 
    # Generate warning message for dashboard
    warning_message = ""
    if today_expense > avg_daily_spend * 1.5 and avg_daily_spend > 0:
        warning_message = f"⚠️ Warning: You spent ₹{today_expense:.0f} today, which is {((today_expense/avg_daily_spend - 1) * 100):.0f}% more than your daily average of ₹{avg_daily_spend:.0f}"
    elif not survive:
        if days_until_broke:
            warning_message = f"⚠️ Warning: Money will run out in {days_until_broke} days at current spending rate"
        else:
            warning_message = "🚨 Critical: Insufficient funds for the month"
    elif health_score < 50:
        warning_message = "🚨 Financial health is at risk - review your spending immediately"
    elif health_score < 70:
        warning_message = "⚠️ Caution: Your spending patterns need attention"
    
    # Get unique categories for filter dropdown
    categories = Transaction.objects.filter(user=request.user).values_list('category', flat=True).distinct().order_by('category')

    context = {
        "transactions": transactions_page,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "upi_balance": upi_balance,
        "hand_balance": hand_balance,
        "start_date": start_date,
        "end_date": end_date,
        "category": category,
        "transaction_type": transaction_type,
        "money_type": money_type,
        "categories": categories,
        "transaction_types": [("INCOME", "Income"), ("EXPENSE", "Expense"), ("SWITCH", "Switch")],
        "money_types": [("UPI CASH", "UPI Cash"), ("HAND CASH", "Hand Cash")],
        "warning_message": warning_message,
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
    
    # Survival warning for analytics
    today = datetime.now().date()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = max(1, today.day)
    days_left = days_in_month - today.day
    
    all_user_transactions = Transaction.objects.filter(user=request.user)
    upi_income = all_user_transactions.filter(transaction_type="INCOME", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
    upi_expense = all_user_transactions.filter(transaction_type="EXPENSE", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
    upi_from_switch = all_user_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
    upi_to_switch = all_user_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
    hand_income = all_user_transactions.filter(transaction_type="INCOME", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
    hand_expense = all_user_transactions.filter(transaction_type="EXPENSE", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
    hand_from_switch = all_user_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
    hand_to_switch = all_user_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
    available_funds = float((upi_income - upi_expense + upi_from_switch - upi_to_switch) + (hand_income - hand_expense + hand_from_switch - hand_to_switch))
    
    current_month_expense = all_user_transactions.filter(date__year=today.year, date__month=today.month, transaction_type="EXPENSE").aggregate(Sum("amount"))["amount__sum"] or 0
    avg_daily_spend = float(current_month_expense) / days_passed if days_passed > 0 else 0
    projected_end_balance = available_funds - (avg_daily_spend * days_left)
    survive = projected_end_balance >= 0
    
    # Today's spending
    today_expense = all_user_transactions.filter(transaction_type="EXPENSE", date=today).aggregate(Sum("amount"))["amount__sum"] or 0
    today_expense = float(today_expense)
    
    days_until_broke = None
    if not survive and avg_daily_spend > 0:
        days_until_broke = int(available_funds / avg_daily_spend)
    
    warning_message = ""
    if today_expense > avg_daily_spend * 1.5 and avg_daily_spend > 0:
        warning_message = f"⚠️ Warning: You spent ₹{today_expense:.0f} today, which is {((today_expense/avg_daily_spend - 1) * 100):.0f}% more than your daily average of ₹{avg_daily_spend:.0f}"
    elif not survive:
        if days_until_broke:
            warning_message = f"⚠️ Warning: Money will run out in {days_until_broke} days at current spending rate"
        else:
            warning_message = "🚨 Critical: Insufficient funds for the month"
    
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
        "warning_message": warning_message,
    }
    
    return render(request, "dashboard/analytics.html", context)


@login_required
def survival_dashboard(request):
    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = max(1, today.day)
    days_left = days_in_month - today.day
    
    # Get current month transactions
    qs = Transaction.objects.filter(user=request.user, date__year=today.year, date__month=today.month)
    
    # Monthly totals
    income_mtd = qs.filter(transaction_type="INCOME").aggregate(Sum("amount"))["amount__sum"] or 0
    expense_mtd = qs.filter(transaction_type="EXPENSE").aggregate(Sum("amount"))["amount__sum"] or 0
    net_mtd = income_mtd - expense_mtd
    
    # Current balances (cumulative from ALL transactions - carries forward from previous months)
    all_transactions = Transaction.objects.filter(user=request.user)
    
    # UPI Cash balance - cumulative from all time including switches
    upi_income = all_transactions.filter(transaction_type="INCOME", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
    upi_expense = all_transactions.filter(transaction_type="EXPENSE", money_type="UPI CASH").aggregate(total=Sum("amount"))["total"] or 0
    upi_from_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
    upi_to_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
    upi_balance = upi_income - upi_expense + upi_from_switch - upi_to_switch
    
    # Hand Cash balance - cumulative from all time including switches
    hand_income = all_transactions.filter(transaction_type="INCOME", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
    hand_expense = all_transactions.filter(transaction_type="EXPENSE", money_type="HAND CASH").aggregate(total=Sum("amount"))["total"] or 0
    hand_from_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="UPI_TO_HAND").aggregate(total=Sum("amount"))["total"] or 0
    hand_to_switch = all_transactions.filter(transaction_type="SWITCH", switch_direction="HAND_TO_UPI").aggregate(total=Sum("amount"))["total"] or 0
    hand_balance = hand_income - hand_expense + hand_from_switch - hand_to_switch
    
    # Survival calculations
    avg_daily_spend = float(expense_mtd) / days_passed if days_passed > 0 else 0
    projected_remaining_spend = avg_daily_spend * days_left
    available_funds = float(upi_balance) + float(hand_balance)
    projected_end_balance = available_funds - projected_remaining_spend
    survive = projected_end_balance >= 0
    
    # Today's spending
    today_expense = qs.filter(transaction_type="EXPENSE", date=today).aggregate(Sum("amount"))["amount__sum"] or 0
    today_expense = float(today_expense)
    
    # Weekly spending analysis
    from datetime import timedelta
    week_start = today - timedelta(days=today.weekday())
    week_expenses = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        if day.month == today.month:
            day_expense = qs.filter(transaction_type="EXPENSE", date=day).aggregate(Sum("amount"))["amount__sum"] or 0
            week_expenses.append({
                'day': day.strftime('%a'),
                'date': day,
                'amount': float(day_expense),
                'is_today': day == today
            })
    
    week_total = sum(d['amount'] for d in week_expenses)
    
    # Health score calculation
    health_score = 100
    if expense_mtd > income_mtd:
        health_score -= 20
    if projected_end_balance < 0:
        health_score -= 30
    if avg_daily_spend > 0 and today_expense > avg_daily_spend * 1.5:
        health_score -= 15
    
    # Health status
    if health_score >= 80:
        health_status = "Healthy ✅"
        health_color = "#2ecc71"
    elif health_score >= 50:
        health_status = "Caution ⚠️"
        health_color = "#f39c12"
    else:
        health_status = "Risk 🚨"
        health_color = "#e74c3c"
    
    # Days until out of money (if applicable)
    days_until_broke = None
    if not survive and avg_daily_spend > 0:
        days_until_broke = int(available_funds / avg_daily_spend)
    
    # Generate warning message
    warning_message = ""
    if today_expense > avg_daily_spend * 1.5 and avg_daily_spend > 0:
        warning_message = f"⚠️ Warning: You spent ₹{today_expense:.0f} today, which is {((today_expense/avg_daily_spend - 1) * 100):.0f}% more than your daily average of ₹{avg_daily_spend:.0f}"
    elif not survive:
        if days_until_broke:
            warning_message = f"⚠️ Warning: Money will run out in {days_until_broke} days at current spending rate"
        else:
            warning_message = "🚨 Critical: Insufficient funds for the month"
    elif health_score < 50:
        warning_message = "🚨 Financial health is at risk - review your spending immediately"
    elif health_score < 70:
        warning_message = "⚠️ Caution: Your spending patterns need attention"
    
    # AI Insights generation
    insights = []
    
    # Compare with last month
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month_transactions = all_transactions.filter(date__year=last_month.year, date__month=last_month.month)
    last_month_expense = last_month_transactions.filter(transaction_type="EXPENSE").aggregate(Sum("amount"))["amount__sum"] or 0
    
    if last_month_expense > 0:
        expense_change = ((float(expense_mtd) - float(last_month_expense)) / float(last_month_expense)) * 100
        if expense_change > 25:
            insights.append(f"📈 You're spending {expense_change:.0f}% more than last month")
        elif expense_change < -15:
            insights.append(f"📉 Great! You've reduced spending by {abs(expense_change):.0f}% from last month")
    
    # Category insights
    current_categories = qs.filter(transaction_type="EXPENSE").values("category").annotate(total=Sum("amount")).order_by("-total")
    last_month_categories = last_month_transactions.filter(transaction_type="EXPENSE").values("category").annotate(total=Sum("amount"))
    
    # Convert to dict for easy lookup
    last_month_dict = {item['category']: float(item['total']) for item in last_month_categories}
    
    for category in current_categories[:3]:  # Top 3 categories
        current_amount = float(category['total'])
        last_amount = last_month_dict.get(category['category'], 0)
        
        if last_amount > 0:
            change = ((current_amount - last_amount) / last_amount) * 100
            if change > 30:
                insights.append(f"🔥 {category['category']} expense spike detected (+{change:.0f}%)")
    
    # Savings insight
    last_month_income = last_month_transactions.filter(transaction_type="INCOME").aggregate(Sum("amount"))["amount__sum"] or 0
    current_savings = float(income_mtd) - float(expense_mtd)
    last_month_savings = float(last_month_income) - float(last_month_expense)
    
    if current_savings > last_month_savings + 1000:
        savings_diff = current_savings - last_month_savings
        insights.append(f"💰 This month you saved ₹{savings_diff:.0f} more than last month")
    
    # High spending day insight
    daily_expenses = qs.filter(transaction_type="EXPENSE").values("date").annotate(total=Sum("amount")).order_by("-total")
    if daily_expenses:
        highest_day = daily_expenses[0]
        if float(highest_day['total']) > avg_daily_spend * 2:
            insights.append(f"📅 Your highest spending day was {highest_day['date'].strftime('%b %d')} (₹{highest_day['total']:.0f})")
    
    # Cashflow forecast
    if survive:
        insights.append(f"✅ At current pace, you'll end the month with ₹{projected_end_balance:.0f}")
    
    # Limit to 3 most relevant insights
    insights = insights[:3]
    
    context = {
        "income_mtd": income_mtd,
        "expense_mtd": expense_mtd,
        "net_mtd": net_mtd,
        "upi_balance": upi_balance,
        "hand_balance": hand_balance,
        "available_funds": available_funds,
        "avg_daily_spend": avg_daily_spend,
        "projected_remaining_spend": projected_remaining_spend,
        "projected_end_balance": projected_end_balance,
        "survive": survive,
        "days_left": days_left,
        "days_until_broke": days_until_broke,
        "health_score": health_score,
        "health_status": health_status,
        "health_color": health_color,
        "days_passed": days_passed,
        "days_in_month": days_in_month,
        "warning_message": warning_message,
        "insights": insights,
        "today_expense": today_expense,
        "week_expenses": week_expenses,
        "week_total": week_total,
    }
    
    return render(request, "dashboard/survival.html", context)
