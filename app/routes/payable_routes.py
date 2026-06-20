"""
Rotas de Contas a Pagar.
"""

from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.controllers import payable_controller, category_controller, supplier_controller, cost_center_controller
from app.controllers.forms import PayableForm, PayablePayForm
from app.middlewares.permission_middleware import can_edit_required, can_delete_required

payable_bp = Blueprint('payable', __name__, template_folder='../templates/payables')


def _populate_choices(form):
    form.supplier_id.choices = [(0, '-- Nenhum --')] + [
        (s.id, s.name) for s in supplier_controller.list_suppliers(per_page=1000).items
    ]
    form.category_id.choices = [(0, '-- Nenhuma --')] + [
        (c.id, c.name) for c in category_controller.list_all_categories()
        if c.type in ('despesa_fixa', 'despesa_variavel', 'imposto', 'investimento', 'outro')
    ]
    form.cost_center_id.choices = [(0, '-- Nenhum --')] + [
        (cc.id, f'{cc.code} - {cc.name}') for cc in cost_center_controller.list_all_cost_centers()
    ]


@payable_bp.route('/')
@login_required
def index():
    query = request.args.get('query', '').strip() or None
    status = request.args.get('status', '').strip() or None
    category_id = request.args.get('category_id', type=int) or None
    supplier_id = request.args.get('supplier_id', type=int) or None
    cost_center_id = request.args.get('cost_center_id', type=int) or None
    date_start_param = request.args.get('date_start')
    date_end_param = request.args.get('date_end')
    page = request.args.get('page', 1, type=int)

    date_start = date.fromisoformat(date_start_param) if date_start_param else None
    date_end = date.fromisoformat(date_end_param) if date_end_param else None

    pagination = payable_controller.list_payables(
        query=query, status=status, category_id=category_id, supplier_id=supplier_id,
        cost_center_id=cost_center_id, date_start=date_start, date_end=date_end, page=page
    )

    categories = category_controller.list_all_categories()
    suppliers = supplier_controller.list_suppliers(per_page=1000).items
    cost_centers = cost_center_controller.list_all_cost_centers()

    return render_template(
        'payables/index.html',
        pagination=pagination,
        items=pagination.items,
        categories=categories,
        suppliers=suppliers,
        cost_centers=cost_centers,
        filters={
            'query': query or '', 'status': status or '', 'category_id': category_id or '',
            'supplier_id': supplier_id or '', 'cost_center_id': cost_center_id or '',
            'date_start': date_start_param or '', 'date_end': date_end_param or '',
        },
    )


@payable_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@can_edit_required
def create():
    form = PayableForm()
    _populate_choices(form)

    if form.validate_on_submit():
        data = {
            'description': form.description.data,
            'amount': form.amount.data,
            'due_date': form.due_date.data,
            'supplier_id': form.supplier_id.data if form.supplier_id.data else None,
            'category_id': form.category_id.data if form.category_id.data else None,
            'cost_center_id': form.cost_center_id.data if form.cost_center_id.data else None,
            'invoice_number': form.invoice_number.data,
            'notes': form.notes.data,
        }
        payable_controller.create_payable(data)
        flash('Conta a pagar cadastrada com sucesso!', 'success')
        return redirect(url_for('payable.index'))

    return render_template('payables/form.html', form=form, title='Nova Conta a Pagar')


@payable_bp.route('/<int:payable_id>/editar', methods=['GET', 'POST'])
@login_required
@can_edit_required
def edit(payable_id):
    payable = payable_controller.get_payable(payable_id)
    form = PayableForm(obj=payable)
    _populate_choices(form)

    if request.method == 'GET':
        form.supplier_id.data = payable.supplier_id or 0
        form.category_id.data = payable.category_id or 0
        form.cost_center_id.data = payable.cost_center_id or 0

    if form.validate_on_submit():
        data = {
            'description': form.description.data,
            'amount': form.amount.data,
            'due_date': form.due_date.data,
            'supplier_id': form.supplier_id.data if form.supplier_id.data else None,
            'category_id': form.category_id.data if form.category_id.data else None,
            'cost_center_id': form.cost_center_id.data if form.cost_center_id.data else None,
            'invoice_number': form.invoice_number.data,
            'notes': form.notes.data,
        }
        payable_controller.update_payable(payable, data)
        flash('Conta a pagar atualizada com sucesso!', 'success')
        return redirect(url_for('payable.index'))

    return render_template('payables/form.html', form=form, title='Editar Conta a Pagar', payable=payable)


@payable_bp.route('/<int:payable_id>')
@login_required
def view(payable_id):
    payable = payable_controller.get_payable(payable_id)
    return render_template('payables/view.html', payable=payable)


@payable_bp.route('/<int:payable_id>/pagar', methods=['GET', 'POST'])
@login_required
@can_edit_required
def pay(payable_id):
    payable = payable_controller.get_payable(payable_id)
    form = PayablePayForm()

    if request.method == 'GET':
        form.paid_amount.data = payable.amount
        form.paid_date.data = date.today()

    if form.validate_on_submit():
        payable_controller.pay_payable(payable, form.paid_amount.data, form.paid_date.data)
        flash('Pagamento registrado com sucesso!', 'success')
        return redirect(url_for('payable.index'))

    return render_template('payables/pay.html', form=form, payable=payable)


@payable_bp.route('/<int:payable_id>/cancelar', methods=['POST'])
@login_required
@can_edit_required
def cancel(payable_id):
    payable = payable_controller.get_payable(payable_id)
    payable_controller.cancel_payable(payable)
    flash('Conta a pagar cancelada.', 'info')
    return redirect(url_for('payable.index'))


@payable_bp.route('/<int:payable_id>/excluir', methods=['POST'])
@login_required
@can_delete_required
def delete(payable_id):
    payable = payable_controller.get_payable(payable_id)
    payable_controller.delete_payable(payable)
    flash('Conta a pagar excluída com sucesso!', 'success')
    return redirect(url_for('payable.index'))
