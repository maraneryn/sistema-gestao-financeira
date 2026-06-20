"""
Rotas de Fluxo de Caixa.
"""

from datetime import date, timedelta

from flask import Blueprint, render_template, request
from flask_login import login_required

from app.services import cashflow_service

cashflow_bp = Blueprint('cashflow', __name__, template_folder='../templates/cashflow')


@cashflow_bp.route('/')
@login_required
def index():
    period = request.args.get('period', 'daily')

    today = date.today()
    date_start_param = request.args.get('date_start')
    date_end_param = request.args.get('date_end')

    if date_start_param:
        date_start = date.fromisoformat(date_start_param)
    else:
        date_start = today - timedelta(days=30)

    if date_end_param:
        date_end = date.fromisoformat(date_end_param)
    else:
        date_end = today

    history = cashflow_service.get_cash_flow_history(date_start, date_end)
    balance_by_period = cashflow_service.get_balance_by_period(period=period, periods_count=12)

    return render_template(
        'cashflow/index.html',
        history=history,
        balance_by_period=balance_by_period,
        period=period,
        date_start=date_start,
        date_end=date_end,
    )


@cashflow_bp.route('/previsao')
@login_required
def forecast():
    days_ahead = int(request.args.get('days', 30))
    forecast_data = cashflow_service.get_financial_forecast(days_ahead=days_ahead)
    return render_template('cashflow/forecast.html', forecast=forecast_data, days_ahead=days_ahead)
