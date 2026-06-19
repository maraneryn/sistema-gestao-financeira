"""
Controller de Fornecedores.
"""

from app.database.connection import db
from app.models.supplier import Supplier
from app.services.audit_service import log_action
from app.services.validators import sanitize_text


def list_suppliers(query: str = None, page: int = 1, per_page: int = 15):
    q = Supplier.query
    if query:
        q = q.filter(
            db.or_(
                Supplier.name.ilike(f'%{query}%'),
                Supplier.document.ilike(f'%{query}%'),
                Supplier.email.ilike(f'%{query}%'),
            )
        )
    return q.order_by(Supplier.name.asc()).paginate(page=page, per_page=per_page, error_out=False)


def get_supplier(supplier_id: int) -> Supplier:
    return Supplier.query.get_or_404(supplier_id)


def create_supplier(data: dict) -> Supplier:
    supplier = Supplier(
        name=sanitize_text(data['name']),
        document=sanitize_text(data.get('document', '')),
        document_type=data.get('document_type', 'CNPJ'),
        email=sanitize_text(data.get('email', '')),
        phone=sanitize_text(data.get('phone', '')),
        address=sanitize_text(data.get('address', '')),
        city=sanitize_text(data.get('city', '')),
        state=sanitize_text(data.get('state', '')),
        zip_code=sanitize_text(data.get('zip_code', '')),
        notes=sanitize_text(data.get('notes', '')),
    )
    db.session.add(supplier)
    db.session.commit()
    log_action('create', 'supplier', supplier.id, f'Fornecedor cadastrado: {supplier.name}')
    return supplier


def update_supplier(supplier: Supplier, data: dict) -> Supplier:
    supplier.name = sanitize_text(data['name'])
    supplier.document = sanitize_text(data.get('document', ''))
    supplier.document_type = data.get('document_type', 'CNPJ')
    supplier.email = sanitize_text(data.get('email', ''))
    supplier.phone = sanitize_text(data.get('phone', ''))
    supplier.address = sanitize_text(data.get('address', ''))
    supplier.city = sanitize_text(data.get('city', ''))
    supplier.state = sanitize_text(data.get('state', ''))
    supplier.zip_code = sanitize_text(data.get('zip_code', ''))
    supplier.notes = sanitize_text(data.get('notes', ''))
    db.session.commit()
    log_action('update', 'supplier', supplier.id, f'Fornecedor atualizado: {supplier.name}')
    return supplier


def delete_supplier(supplier: Supplier) -> tuple:
    if supplier.payables.count() > 0:
        return False, 'Não é possível excluir um fornecedor com contas a pagar vinculadas. Desative-o ao invés disso.'
    name = supplier.name
    supplier_id = supplier.id
    db.session.delete(supplier)
    db.session.commit()
    log_action('delete', 'supplier', supplier_id, f'Fornecedor excluído: {name}')
    return True, 'Fornecedor excluído com sucesso.'


def toggle_supplier_status(supplier: Supplier) -> Supplier:
    supplier.is_active = not supplier.is_active
    db.session.commit()
    status = 'ativado' if supplier.is_active else 'desativado'
    log_action('toggle_status', 'supplier', supplier.id, f'Fornecedor {status}: {supplier.name}')
    return supplier
