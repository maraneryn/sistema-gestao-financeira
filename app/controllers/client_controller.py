"""
Controller de Clientes.
"""

from app.database.connection import db
from app.models.client import Client
from app.services.audit_service import log_action
from app.services.validators import sanitize_text


def list_clients(query: str = None, page: int = 1, per_page: int = 15):
    q = Client.query
    if query:
        q = q.filter(
            db.or_(
                Client.name.ilike(f'%{query}%'),
                Client.document.ilike(f'%{query}%'),
                Client.email.ilike(f'%{query}%'),
            )
        )
    return q.order_by(Client.name.asc()).paginate(page=page, per_page=per_page, error_out=False)


def get_client(client_id: int) -> Client:
    return Client.query.get_or_404(client_id)


def create_client(data: dict) -> Client:
    client = Client(
        name=sanitize_text(data['name']),
        document=sanitize_text(data.get('document', '')),
        document_type=data.get('document_type', 'CPF'),
        email=sanitize_text(data.get('email', '')),
        phone=sanitize_text(data.get('phone', '')),
        address=sanitize_text(data.get('address', '')),
        city=sanitize_text(data.get('city', '')),
        state=sanitize_text(data.get('state', '')),
        zip_code=sanitize_text(data.get('zip_code', '')),
        notes=sanitize_text(data.get('notes', '')),
    )
    db.session.add(client)
    db.session.commit()
    log_action('create', 'client', client.id, f'Cliente cadastrado: {client.name}')
    return client


def update_client(client: Client, data: dict) -> Client:
    client.name = sanitize_text(data['name'])
    client.document = sanitize_text(data.get('document', ''))
    client.document_type = data.get('document_type', 'CPF')
    client.email = sanitize_text(data.get('email', ''))
    client.phone = sanitize_text(data.get('phone', ''))
    client.address = sanitize_text(data.get('address', ''))
    client.city = sanitize_text(data.get('city', ''))
    client.state = sanitize_text(data.get('state', ''))
    client.zip_code = sanitize_text(data.get('zip_code', ''))
    client.notes = sanitize_text(data.get('notes', ''))
    db.session.commit()
    log_action('update', 'client', client.id, f'Cliente atualizado: {client.name}')
    return client


def delete_client(client: Client) -> tuple:
    if client.receivables.count() > 0:
        return False, 'Não é possível excluir um cliente com contas a receber vinculadas. Desative-o ao invés disso.'
    name = client.name
    client_id = client.id
    db.session.delete(client)
    db.session.commit()
    log_action('delete', 'client', client_id, f'Cliente excluído: {name}')
    return True, 'Cliente excluído com sucesso.'


def toggle_client_status(client: Client) -> Client:
    client.is_active = not client.is_active
    db.session.commit()
    status = 'ativado' if client.is_active else 'desativado'
    log_action('toggle_status', 'client', client.id, f'Cliente {status}: {client.name}')
    return client
