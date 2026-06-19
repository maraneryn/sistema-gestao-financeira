"""
Serviço de fluxo de caixa: histórico de movimentações e previsão financeira.
"""

from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func
from app.database.connection import db
from app.models.receivable import Receivable
from app.models.payable import Payable


def get_cash_flow_history(start_date: date, end_date: date) -> list:
    """Retorna o histórico diário de entradas e saídas no período informado."""
    history = []
    current = start_date
    running_balance = _get_balance_before(start_date)

    while current <= end_date:
        inflow = db.session.query(func.sum(Receivable.received_amount)).filter(
            Receivable.received_date == current,
            Receivable.status.in_(['recebido', 'parcial'])
        ).scalar() or Decimal('0')

        outflow = db.session.query(func.sum(Payable.paid_amount)).filter(
            Payable.paid_date == current,
            Payable.status.in_(['pago', 'parcial'])
        ).scalar() or Decimal('0')

        day_net = inflow - outflow
        running_balance += day_net

        history.append({
            'date': current,
            'inflow': float(inflow),
            'outflow': float(outflow),
            'net': float(day_net),
            'balance': float(running_balance),
        })

        current += timedelta(days=1)

    return history


def _get_balance_before(start_date: date) -> Decimal:
    inflow = db.session.query(func.sum(Receivable.received_amount)).filter(
        Receivable.received_date < start_date,
        Receivable.status.in_(['recebido', 'parcial'])
    ).scalar() or Decimal('0')

    outflow = db.session.query(func.sum(Payable.paid_amount)).filter(
        Payable.paid_date < start_date,
        Payable.status.in_(['pago', 'parcial'])
    ).scalar() or Decimal('0')

    return inflow - outflow


def get_financial_forecast(days_ahead: int = 30) -> dict:
    """Gera previsão financeira com base em contas pendentes."""
    today = date.today()
    forecast_end = today + timedelta(days=days_ahead)

    pending_receivables = Receivable.query.filter(
        Receivable.status == 'pendente',
        Receivable.due_date >= today,
        Receivable.due_date <= forecast_end
    ).order_by(Receivable.due_date).all()

    pending_payables = Payable.query.filter(
        Payable.status == 'pendente',
        Payable.due_date >= today,
        Payable.due_date <= forecast_end
    ).order_by(Payable.due_date).all()

    total_expected_in = sum(float(r.amount) for r in pending_receivables)
    total_expected_out = sum(float(p.amount) for p in pending_payables)

    timeline = {}
    for r in pending_receivables:
        key = r.due_date.isoformat()
        timeline.setdefault(key, {'date': r.due_date, 'inflow': 0.0, 'outflow': 0.0})
        timeline[key]['inflow'] += float(r.amount)

    for p in pending_payables:
        key = p.due_date.isoformat()
        timeline.setdefault(key, {'date': p.due_date, 'inflow': 0.0, 'outflow': 0.0})
        timeline[key]['outflow'] += float(p.amount)

    sorted_timeline = sorted(timeline.values(), key=lambda x: x['date'])

    return {
        'total_expected_in': total_expected_in,
        'total_expected_out': total_expected_out,
        'projected_net': total_expected_in - total_expected_out,
        'timeline': sorted_timeline,
        'pending_receivables': pending_receivables,
        'pending_payables': pending_payables,
    }


def get_balance_by_period(period: str = 'daily', periods_count: int = 30) -> list:
    """Retorna saldo agregado por dia, semana, mês ou ano."""
    today = date.today()

    if period == 'daily':
        start = today - timedelta(days=periods_count)
        return get_cash_flow_history(start, today)

    if period == 'weekly':
        result = []
        for i in range(periods_count, 0, -1):
            week_end = today - timedelta(days=(i - 1) * 7)
            week_start = week_end - timedelta(days=6)
            history = get_cash_flow_history(week_start, week_end)
            total_in = sum(h['inflow'] for h in history)
            total_out = sum(h['outflow'] for h in history)
            result.append({
                'label': f'{week_start.strftime("%d/%m")} - {week_end.strftime("%d/%m")}',
                'inflow': total_in,
                'outflow': total_out,
                'net': total_in - total_out,
            })
        return result

    if period == 'monthly':
        result = []
        for i in range(periods_count, 0, -1):
            ref_month = today.month - (i - 1)
            ref_year = today.year
            while ref_month <= 0:
                ref_month += 12
                ref_year -= 1
            month_start = date(ref_year, ref_month, 1)
            if ref_month == 12:
                month_end = date(ref_year, 12, 31)
            else:
                month_end = date(ref_year, ref_month + 1, 1) - timedelta(days=1)
            history = get_cash_flow_history(month_start, min(month_end, today))
            total_in = sum(h['inflow'] for h in history)
            total_out = sum(h['outflow'] for h in history)
            result.append({
                'label': month_start.strftime('%m/%Y'),
                'inflow': total_in,
                'outflow': total_out,
                'net': total_in - total_out,
            })
        return result

    return []
