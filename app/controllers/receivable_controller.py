"""
Controller de Contas a Receber.
"""

from datetime import date
from flask_login import current_user

from app.database.connection import db
from app.models.receivable import Receivable
from app.services.audit_service import log_action
from app.services.validators import sanitize_text


def list_receivables(query: str = None, status: str = None, category_id: int = None,
                      client_id: int = None, date_start: date = None, date_end: date = None,
                      page: int = 1, per_page: int = 15):
    """Lista contas a receber com filtros opcionais e paginação."""
    _update_overdue_status()

    q = Receivable.query

    if query:
        q = q.filter(Receivable.description.ilike(f'%{query}%'))
    if status:
        q = q.filter(Receivable.status == status)
    if category_id:
        q = q.filter(Receivable.category_id == category_id)
    if client_id:
        q = q.filter(Receivable.client_id == client_id)
    if date_start:
        q = q.filter(Receivable.due_date >= date_start)
    if date_end:
        q = q.filter(Receivable.due_date <= date_end)

    return q.order_by(Receivable.due_date.asc()).paginate(page=page, per_page=per_page, error_out=False)


def _update_overdue_status() -> None:
    """Atualiza automaticamente o status de contas vencidas."""
    today = date.today()
    overdue = Receivable.query.filter(
        Receivable.status == 'pendente',
        Receivable.due_date < today
    ).all()
    for item in overdue:
        item.status = 'vencido'
    if overdue:
        db.session.commit()


def get_receivable(receivable_id: int) -> Receivable:
    return Receivable.query.get_or_404(receivable_id)


def create_receivable(data: dict) -> Receivable:
    receivable = Receivable(
        description=sanitize_text(data['description']),
        amount=data['amount'],
        due_date=data['due_date'],
        client_id=data.get('client_id') or None,
        category_id=data.get('category_id') or None,
        invoice_number=sanitize_text(data.get('invoice_number', '')),
        notes=sanitize_text(data.get('notes', '')),
        status='pendente',
        created_by=current_user.id if current_user.is_authenticated else None,
    )
    db.session.add(receivable)
    db.session.commit()
    log_action('create', 'receivable', receivable.id, f'Conta a receber criada: {receivable.description}')
    return receivable


def update_receivable(receivable: Receivable, data: dict) -> Receivable:
    receivable.description = sanitize_text(data['description'])
    receivable.amount = data['amount']
    receivable.due_date = data['due_date']
    receivable.client_id = data.get('client_id') or None
    receivable.category_id = data.get('category_id') or None
    receivable.invoice_number = sanitize_text(data.get('invoice_number', ''))
    receivable.notes = sanitize_text(data.get('notes', ''))

    if receivable.status == 'vencido' and receivable.due_date >= date.today():
        receivable.status = 'pendente'

    db.session.commit()
    log_action('update', 'receivable', receivable.id, f'Conta a receber atualizada: {receivable.description}')
    return receivable


def delete_receivable(receivable: Receivable) -> None:
    description = receivable.description
    receivable_id = receivable.id
    db.session.delete(receivable)
    db.session.commit()
    log_action('delete', 'receivable', receivable_id, f'Conta a receber excluída: {description}')


def receive_payment(receivable: Receivable, received_amount, received_date) -> Receivable:
    receivable.mark_as_received(received_amount, received_date)
    db.session.commit()
    log_action('receive', 'receivable', receivable.id, f'Recebimento registrado: {receivable.description}')
    return receivable


def cancel_receivable(receivable: Receivable) -> Receivable:
    receivable.status = 'cancelado'
    db.session.commit()
    log_action('cancel', 'receivable', receivable.id, f'Conta a receber cancelada: {receivable.description}')
    return receivable
