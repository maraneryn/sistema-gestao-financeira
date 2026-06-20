"""
Rotas de Relatórios Gerenciais (PDF, Excel, CSV).
"""

from datetime import date, timedelta

from flask import Blueprint, render_template, request, send_file
from flask_login import login_required

from app.models.receivable import Receivable
from app.models.payable import Payable
from app.services import report_service, dashboard_service
from app.services.audit_service import log_action

report_bp = Blueprint('report', __name__, template_folder='../templates/reports')


def _get_filtered_data(date_start, date_end):
    receivables = Receivable.query.filter(
        Receivable.due_date >= date_start, Receivable.due_date <= date_end
    ).order_by(Receivable.due_date).all()

    payables = Payable.query.filter(
        Payable.due_date >= date_start, Payable.due_date <= date_end
    ).order_by(Payable.due_date).all()

    return receivables, payables


@report_bp.route('/')
@login_required
def index():
    summary = dashboard_service.get_dashboard_summary()
    return render_template('reports/index.html', summary=summary)


@report_bp.route('/financeiro/pdf')
@login_required
def financial_pdf():
    date_start, date_end = _parse_date_range()
    receivables, payables = _get_filtered_data(date_start, date_end)

    headers = ['Tipo', 'Descrição', 'Valor (R$)', 'Vencimento', 'Status']
    rows = []
    for r in receivables:
        rows.append(['Receita', r.description, f'{r.amount:.2f}', r.due_date.strftime('%d/%m/%Y'), r.status_label])
    for p in payables:
        rows.append(['Despesa', p.description, f'{p.amount:.2f}', p.due_date.strftime('%d/%m/%Y'), p.status_label])

    total_receivable = sum(float(r.amount) for r in receivables)
    total_payable = sum(float(p.amount) for p in payables)

    summary = {
        'Total de Receitas': f'R$ {total_receivable:,.2f}',
        'Total de Despesas': f'R$ {total_payable:,.2f}',
        'Saldo do Período': f'R$ {(total_receivable - total_payable):,.2f}',
        'Período': f'{date_start.strftime("%d/%m/%Y")} a {date_end.strftime("%d/%m/%Y")}',
    }

    buffer = report_service.generate_pdf_report('Relatório Financeiro', headers, rows, summary)
    log_action('export', 'report', None, 'Exportação de relatório financeiro em PDF')

    return send_file(
        buffer, mimetype='application/pdf', as_attachment=True,
        download_name=f'relatorio_financeiro_{date.today().isoformat()}.pdf'
    )


@report_bp.route('/financeiro/excel')
@login_required
def financial_excel():
    date_start, date_end = _parse_date_range()
    receivables, payables = _get_filtered_data(date_start, date_end)

    headers = ['Tipo', 'Descrição', 'Valor (R$)', 'Vencimento', 'Status']
    rows = []
    for r in receivables:
        rows.append(['Receita', r.description, float(r.amount), r.due_date.strftime('%d/%m/%Y'), r.status_label])
    for p in payables:
        rows.append(['Despesa', p.description, float(p.amount), p.due_date.strftime('%d/%m/%Y'), p.status_label])

    buffer = report_service.generate_excel_report('Relatorio Financeiro', headers, rows)
    log_action('export', 'report', None, 'Exportação de relatório financeiro em Excel')

    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'relatorio_financeiro_{date.today().isoformat()}.xlsx'
    )


@report_bp.route('/financeiro/csv')
@login_required
def financial_csv():
    date_start, date_end = _parse_date_range()
    receivables, payables = _get_filtered_data(date_start, date_end)

    headers = ['Tipo', 'Descrição', 'Valor (R$)', 'Vencimento', 'Status']
    rows = []
    for r in receivables:
        rows.append(['Receita', r.description, f'{r.amount:.2f}', r.due_date.strftime('%d/%m/%Y'), r.status_label])
    for p in payables:
        rows.append(['Despesa', p.description, f'{p.amount:.2f}', p.due_date.strftime('%d/%m/%Y'), p.status_label])

    buffer = report_service.generate_csv_report(headers, rows)
    log_action('export', 'report', None, 'Exportação de relatório financeiro em CSV')

    csv_bytes = buffer.getvalue().encode('utf-8-sig')
    import io as io_module
    byte_buffer = io_module.BytesIO(csv_bytes)

    return send_file(
        byte_buffer, mimetype='text/csv', as_attachment=True,
        download_name=f'relatorio_financeiro_{date.today().isoformat()}.csv'
    )


@report_bp.route('/receber/pdf')
@login_required
def receivables_pdf():
    receivables = Receivable.query.order_by(Receivable.due_date).all()
    headers = ['Descrição', 'Cliente', 'Valor (R$)', 'Vencimento', 'Status']
    rows = [
        [r.description, r.client.name if r.client else '-', f'{r.amount:.2f}',
         r.due_date.strftime('%d/%m/%Y'), r.status_label]
        for r in receivables
    ]
    buffer = report_service.generate_pdf_report('Relatório de Contas a Receber', headers, rows)
    log_action('export', 'report', None, 'Exportação de contas a receber em PDF')

    return send_file(
        buffer, mimetype='application/pdf', as_attachment=True,
        download_name=f'contas_a_receber_{date.today().isoformat()}.pdf'
    )


@report_bp.route('/pagar/pdf')
@login_required
def payables_pdf():
    payables = Payable.query.order_by(Payable.due_date).all()
    headers = ['Descrição', 'Fornecedor', 'Valor (R$)', 'Vencimento', 'Status']
    rows = [
        [p.description, p.supplier.name if p.supplier else '-', f'{p.amount:.2f}',
         p.due_date.strftime('%d/%m/%Y'), p.status_label]
        for p in payables
    ]
    buffer = report_service.generate_pdf_report('Relatório de Contas a Pagar', headers, rows)
    log_action('export', 'report', None, 'Exportação de contas a pagar em PDF')

    return send_file(
        buffer, mimetype='application/pdf', as_attachment=True,
        download_name=f'contas_a_pagar_{date.today().isoformat()}.pdf'
    )


def _parse_date_range():
    date_start_param = request.args.get('date_start')
    date_end_param = request.args.get('date_end')

    date_start = date.fromisoformat(date_start_param) if date_start_param else date.today().replace(day=1)
    date_end = date.fromisoformat(date_end_param) if date_end_param else date.today()

    return date_start, date_end
