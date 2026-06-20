"""
Rotas do Dashboard Executivo.
"""

from flask import Blueprint, render_template
from flask_login import login_required

from app.services import dashboard_service

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    summary = dashboard_service.get_dashboard_summary()
    monthly_evolution = dashboard_service.get_monthly_evolution()
    annual_evolution = dashboard_service.get_annual_evolution()
    recent = dashboard_service.get_recent_transactions(limit=8)
    cash_flow = dashboard_service.get_cash_flow_summary()

    return render_template(
        'dashboard/index.html',
        summary=summary,
        monthly_evolution=monthly_evolution,
        annual_evolution=annual_evolution,
        recent=recent,
        cash_flow=cash_flow,
    )
