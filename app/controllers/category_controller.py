"""
Controller de Categorias Financeiras.
"""

from app.database.connection import db
from app.models.category import Category
from app.services.audit_service import log_action
from app.services.validators import sanitize_text


def list_categories(query: str = None, type_filter: str = None, page: int = 1, per_page: int = 15):
    q = Category.query
    if query:
        q = q.filter(Category.name.ilike(f'%{query}%'))
    if type_filter:
        q = q.filter(Category.type == type_filter)
    return q.order_by(Category.type.asc(), Category.name.asc()).paginate(page=page, per_page=per_page, error_out=False)


def list_all_categories(type_filter: str = None):
    """Lista todas as categorias ativas, sem paginação (para uso em selects)."""
    q = Category.query.filter_by(is_active=True)
    if type_filter:
        q = q.filter(Category.type == type_filter)
    return q.order_by(Category.name.asc()).all()


def get_category(category_id: int) -> Category:
    return Category.query.get_or_404(category_id)


def create_category(data: dict) -> Category:
    category = Category(
        name=sanitize_text(data['name']),
        type=data['type'],
        description=sanitize_text(data.get('description', '')),
        color=data.get('color') or '#007bff',
        icon=data.get('icon') or 'bi-tag',
    )
    db.session.add(category)
    db.session.commit()
    log_action('create', 'category', category.id, f'Categoria criada: {category.name}')
    return category


def update_category(category: Category, data: dict) -> Category:
    category.name = sanitize_text(data['name'])
    category.type = data['type']
    category.description = sanitize_text(data.get('description', ''))
    category.color = data.get('color') or '#007bff'
    category.icon = data.get('icon') or 'bi-tag'
    db.session.commit()
    log_action('update', 'category', category.id, f'Categoria atualizada: {category.name}')
    return category


def delete_category(category: Category) -> tuple:
    if category.receivables.count() > 0 or category.payables.count() > 0:
        return False, 'Não é possível excluir uma categoria com lançamentos vinculados. Desative-a ao invés disso.'
    name = category.name
    category_id = category.id
    db.session.delete(category)
    db.session.commit()
    log_action('delete', 'category', category_id, f'Categoria excluída: {name}')
    return True, 'Categoria excluída com sucesso.'


def toggle_category_status(category: Category) -> Category:
    category.is_active = not category.is_active
    db.session.commit()
    status = 'ativada' if category.is_active else 'desativada'
    log_action('toggle_status', 'category', category.id, f'Categoria {status}: {category.name}')
    return category
