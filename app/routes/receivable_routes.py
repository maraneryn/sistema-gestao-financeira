"""
Rotas de Contas a Receber.
"""

from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.controllers import receivable_controller, category_controller, client_controller
from app.controllers.forms import ReceivableForm, ReceivableReceiveForm
from app.middlewares.permission_middleware import can_edit_required, can_delete_required

receivable_bp = Blueprint('receivable', __name__, template_folder='../templates/receivables')


def _populate_choices(form):
    form.client_id.choices = [(0, '-- Nenhum --')] + [
        (c.id, c.name) for c in client_controller.list_clients(per_page=1000).items
    ]
    form.category_id.choices = [(0, '-- Nenhuma --')] + [
        (c.id, c.name) for c in category_controller.list_all_categories(type_filter='receita')
    ]


@receivable_bp.route('/')
@login_required
def index():
    query = request.args.get('query', '').strip() or None
    status = request.args.get('status', '').strip() or None
    category_id = request.args.get('category_id', type=int) or None
    client_id = request.args.get('client_id', type=int) or None
    date_start_param = request.args.get('date_start')
    date_end_param = request.args.get('date_end')
    page = request.args.get('page', 1, type=int)

    date_start = date.fromisoformat(date_start_param) if date_start_param else None
    date_end = date.fromisoformat(date_end_param) if date_end_param else None

    pagination = receivable_controller.list_receivables(
        query=query, status=status, category_id=category_id, client_id=client_id,
        date_start=date_start, date_end=date_end, page=page
    )

    categories = category_controller.list_all_categories(type_filter='receita')
    clients = client_controller.list_clients(per_page=1000).items

    return render_template(
        'receivables/index.html',
        pagination=pagination,
        items=pagination.items,
        categories=categories,
        clients=clients,
        filters={
            'query': query or '', 'status': status or '', 'category_id': category_id or '',
            'client_id': client_id or '', 'date_start': date_start_param or '', 'date_end': date_end_param or '',
        },
    )


@receivable_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@can_edit_required
def create():
    form = ReceivableForm()
    _populate_choices(form)

    if form.validate_on_submit():
        data = {
            'description': form.description.data,
            'amount': form.amount.data,
            'due_date': form.due_date.data,
            'client_id': form.client_id.data if form.client_id.data else None,
            'category_id': form.category_id.data if form.category_id.data else None,
            'invoice_number': form.invoice_number.data,
            'notes': form.notes.data,
        }
        receivable_controller.create_receivable(data)
        flash('Conta a receber cadastrada com sucesso!', 'success')
        return redirect(url_for('receivable.index'))

    return render_template('receivables/form.html', form=form, title='Nova Conta a Receber')


@receivable_bp.route('/<int:receivable_id>/editar', methods=['GET', 'POST'])
@login_required
@can_edit_required
def edit(receivable_id):
    receivable = receivable_controller.get_receivable(receivable_id)
    form = ReceivableForm(obj=receivable)
    _populate_choices(form)

    if request.method == 'GET':
        form.client_id.data = receivable.client_id or 0
        form.category_id.data = receivable.category_id or 0

    if form.validate_on_submit():
        data = {
            'description': form.description.data,
            'amount': form.amount.data,
            'due_date': form.due_date.data,
            'client_id': form.client_id.data if form.client_id.data else None,
            'category_id': form.category_id.data if form.category_id.data else None,
            'invoice_number': form.invoice_number.data,
            'notes': form.notes.data,
        }
        receivable_controller.update_receivable(receivable, data)
        flash('Conta a receber atualizada com sucesso!', 'success')
        return redirect(url_for('receivable.index'))

    return render_template('receivables/form.html', form=form, title='Editar Conta a Receber', receivable=receivable)


@receivable_bp.route('/<int:receivable_id>')
@login_required
def view(receivable_id):
    receivable = receivable_controller.get_receivable(receivable_id)
    return render_template('receivables/view.html', receivable=receivable)


@receivable_bp.route('/<int:receivable_id>/receber', methods=['GET', 'POST'])
@login_required
@can_edit_required
def receive(receivable_id):
    receivable = receivable_controller.get_receivable(receivable_id)
    form = ReceivableReceiveForm()

    if request.method == 'GET':
        form.received_amount.data = receivable.amount
        form.received_date.data = date.today()

    if form.validate_on_submit():
        receivable_controller.receive_payment(receivable, form.received_amount.data, form.received_date.data)
        flash('Recebimento registrado com sucesso!', 'success')
        return redirect(url_for('receivable.index'))

    return render_template('receivables/receive.html', form=form, receivable=receivable)


@receivable_bp.route('/<int:receivable_id>/cancelar', methods=['POST'])
@login_required
@can_edit_required
def cancel(receivable_id):
    receivable = receivable_controller.get_receivable(receivable_id)
    receivable_controller.cancel_receivable(receivable)
    flash('Conta a receber cancelada.', 'info')
    return redirect(url_for('receivable.index'))


@receivable_bp.route('/<int:receivable_id>/excluir', methods=['POST'])
@login_required
@can_delete_required
def delete(receivable_id):
    receivable = receivable_controller.get_receivable(receivable_id)
    receivable_controller.delete_receivable(receivable)
    flash('Conta a receber excluída com sucesso!', 'success')
    return redirect(url_for('receivable.index'))
