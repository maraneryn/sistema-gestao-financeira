"""
Serviço de dados para o dashboard executivo.
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, extract
from app.database.connection import db
from app.models.receivable import Receivable
from app.models.payable import Payable


def get_dashboard_summary() -> dict:
    """Retorna resumo financeiro para o dashboard."""
    today = date.today()
    current_month = today.month
    current_year = today.year

    total_receivable_pending = _sum_amount(Receivable, status='pendente')
    total_payable_pending = _sum_amount(Payable, status='pendente')

    month_revenue = _sum_month(Receivable, current_month, current_year, status='recebido')
    month_expenses = _sum_month(Payable, current_month, current_year, status='pago')
    month_net = month_revenue - month_expenses

    year_revenue = _sum_year(Receivable, current_year, status='recebido')
    year_expenses = _sum_year(Payable, current_year, status='pago')
    year_net = year_revenue - year_expenses

    overdue_receivables = Receivable.query.filter(
        Receivable.status == 'pendente',
        Receivable.due_date < today
    ).count()

    overdue_payables = Payable.query.filter(
        Payable.status == 'pendente',
        Payable.due_date < today
    ).count()

    due_week = today + timedelta(days=7)
    receivables_week = Receivable.query.filter(
        Receivable.status == 'pendente',
        Receivable.due_date <= due_week,
        Receivable.due_date >= today
    ).count()

    payables_week = Payable.query.filter(
        Payable.status == 'pendente',
        Payable.due_date <= due_week,
        Payable.due_date >= today
    ).count()

    return {
        'total_receivable_pending': float(total_receivable_pending),
        'total_payable_pending': float(total_payable_pending),
        'balance': float(total_receivable_pending - total_payable_pending),
        'month_revenue': float(month_revenue),
        'month_expenses': float(month_expenses),
        'month_net': float(month_net),
        'year_revenue': float(year_revenue),
        'year_expenses': float(year_expenses),
        'year_net': float(year_net),
        'overdue_receivables': overdue_receivables,
        'overdue_payables': overdue_payables,
        'receivables_week': receivables_week,
        'payables_week': payables_week,
    }


def get_monthly_evolution(year: int = None) -> list:
    """Retorna evolução mensal de receitas e despesas."""
    year = year or date.today().year
    months = []

    for month in range(1, 13):
        revenue = float(_sum_month(Receivable, month, year, status='recebido'))
        expenses = float(_sum_month(Payable, month, year, status='pago'))
        months.append({
            'month': month,
            'month_name': _month_name(month),
            'revenue': revenue,
            'expenses': expenses,
            'net': revenue - expenses,
        })

    return months


def get_annual_evolution(years: int = 5) -> list:
    """Retorna evolução anual dos últimos N anos."""
    current_year = date.today().year
    result = []

    for year in range(current_year - years + 1, current_year + 1):
        revenue = float(_sum_year(Receivable, year, status='recebido'))
        expenses = float(_sum_year(Payable, year, status='pago'))
        result.append({
            'year': year,
            'revenue': revenue,
            'expenses': expenses,
            'net': revenue - expenses,
        })

    return result


def get_recent_transactions(limit: int = 10) -> dict:
    """Retorna transações recentes."""
    recent_receivables = Receivable.query.order_by(
        Receivable.created_at.desc()
    ).limit(limit).all()

    recent_payables = Payable.query.order_by(
        Payable.created_at.desc()
    ).limit(limit).all()

    return {
        'receivables': recent_receivables,
        'payables': recent_payables,
    }


def get_cash_flow_summary() -> dict:
    """Retorna resumo do fluxo de caixa."""
    today = date.today()

    daily = _cash_flow_period(
        date(today.year, today.month, today.day),
        date(today.year, today.month, today.day)
    )

    week_start = today - timedelta(days=today.weekday())
    weekly = _cash_flow_period(week_start, today)

    month_start = date(today.year, today.month, 1)
    monthly = _cash_flow_period(month_start, today)

    year_start = date(today.year, 1, 1)
    annual = _cash_flow_period(year_start, today)

    return {
        'daily': daily,
        'weekly': weekly,
        'monthly': monthly,
        'annual': annual,
    }


def _cash_flow_period(start: date, end: date) -> dict:
    revenue = db.session.query(func.sum(Receivable.received_amount)).filter(
        Receivable.received_date >= start,
        Receivable.received_date <= end,
        Receivable.status.in_(['recebido', 'parcial'])
    ).scalar() or Decimal('0')

    expenses = db.session.query(func.sum(Payable.paid_amount)).filter(
        Payable.paid_date >= start,
        Payable.paid_date <= end,
        Payable.status.in_(['pago', 'parcial'])
    ).scalar() or Decimal('0')

    return {
        'revenue': float(revenue),
        'expenses': float(expenses),
        'net': float(revenue - expenses),
    }


def _sum_amount(model, status: str) -> Decimal:
    result = db.session.query(func.sum(model.amount)).filter(
        model.status == status
    ).scalar()
    return result or Decimal('0')


def _sum_month(model, month: int, year: int, status: str) -> Decimal:
    amount_col = model.received_amount if model == Receivable else model.paid_amount
    date_col = model.received_date if model == Receivable else model.paid_date

    result = db.session.query(func.sum(amount_col)).filter(
        extract('month', date_col) == month,
        extract('year', date_col) == year,
        model.status.in_([status, 'parcial'])
    ).scalar()
    return result or Decimal('0')


def _sum_year(model, year: int, status: str) -> Decimal:
    amount_col = model.received_amount if model == Receivable else model.paid_amount
    date_col = model.received_date if model == Receivable else model.paid_date

    result = db.session.query(func.sum(amount_col)).filter(
        extract('year', date_col) == year,
        model.status.in_([status, 'parcial'])
    ).scalar()
    return result or Decimal('0')


def _month_name(month: int) -> str:
    names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    return names[month - 1]
