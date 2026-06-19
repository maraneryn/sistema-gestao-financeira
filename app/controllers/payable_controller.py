"""
Controller de Contas a Pagar.
"""

from datetime import date
from flask_login import current_user

from app.database.connection import db
from app.models.payable import Payable
from app.services.audit_service import log_action
from app.services.validators import sanitize_text


def list_payables(query: str = None, status: str = None, category_id: int = None,
                   supplier_id: int = None, cost_center_id: int = None,
                   date_start: date = None, date_end: date = None,
                   page: int = 1, per_page: int = 15):
    """Lista contas a pagar com filtros opcionais e paginação."""
    _update_overdue_status()

    q = Payable.query

    if query:
        q = q.filter(Payable.description.ilike(f'%{query}%'))
    if status:
        q = q.filter(Payable.status == status)
    if category_id:
        q = q.filter(Payable.category_id == category_id)
    if supplier_id:
        q = q.filter(Payable.supplier_id == supplier_id)
    if cost_center_id:
        q = q.filter(Payable.cost_center_id == cost_center_id)
    if date_start:
        q = q.filter(Payable.due_date >= date_start)
    if date_end:
        q = q.filter(Payable.due_date <= date_end)

    return q.order_by(Payable.due_date.asc()).paginate(page=page, per_page=per_page, error_out=False)


def _update_overdue_status() -> None:
    today = date.today()
    overdue = Payable.query.filter(
        Payable.status == 'pendente',
        Payable.due_date < today
    ).all()
    for item in overdue:
        item.status = 'vencido'
    if overdue:
        db.session.commit()


def get_payable(payable_id: int) -> Payable:
    return Payable.query.get_or_404(payable_id)


def create_payable(data: dict) -> Payable:
    payable = Payable(
        description=sanitize_text(data['description']),
        amount=data['amount'],
        due_date=data['due_date'],
        supplier_id=data.get('supplier_id') or None,
        category_id=data.get('category_id') or None,
        cost_center_id=data.get('cost_center_id') or None,
        invoice_number=sanitize_text(data.get('invoice_number', '')),
        notes=sanitize_text(data.get('notes', '')),
        status='pendente',
        created_by=current_user.id if current_user.is_authenticated else None,
    )
    db.session.add(payable)
    db.session.commit()
    log_action('create', 'payable', payable.id, f'Conta a pagar criada: {payable.description}')
    return payable


def update_payable(payable: Payable, data: dict) -> Payable:
    payable.description = sanitize_text(data['description'])
    payable.amount = data['amount']
    payable.due_date = data['due_date']
    payable.supplier_id = data.get('supplier_id') or None
    payable.category_id = data.get('category_id') or None
    payable.cost_center_id = data.get('cost_center_id') or None
    payable.invoice_number = sanitize_text(data.get('invoice_number', ''))
    payable.notes = sanitize_text(data.get('notes', ''))

    if payable.status == 'vencido' and payable.due_date >= date.today():
        payable.status = 'pendente'

    db.session.commit()
    log_action('update', 'payable', payable.id, f'Conta a pagar atualizada: {payable.description}')
    return payable


def delete_payable(payable: Payable) -> None:
    description = payable.description
    payable_id = payable.id
    db.session.delete(payable)
    db.session.commit()
    log_action('delete', 'payable', payable_id, f'Conta a pagar excluída: {description}')


def pay_payable(payable: Payable, paid_amount, paid_date) -> Payable:
    payable.mark_as_paid(paid_amount, paid_date)
    db.session.commit()
    log_action('pay', 'payable', payable.id, f'Pagamento registrado: {payable.description}')
    return payable


def cancel_payable(payable: Payable) -> Payable:
    payable.status = 'cancelado'
    db.session.commit()
    log_action('cancel', 'payable', payable.id, f'Conta a pagar cancelada: {payable.description}')
    return payable
