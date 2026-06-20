"""
Controller de Centro de Custos.
"""

from app.database.connection import db
from app.models.cost_center import CostCenter
from app.services.audit_service import log_action
from app.services.validators import sanitize_text


def list_cost_centers(query: str = None, page: int = 1, per_page: int = 15):
    q = CostCenter.query
    if query:
        q = q.filter(
            db.or_(
                CostCenter.name.ilike(f'%{query}%'),
                CostCenter.code.ilike(f'%{query}%'),
                CostCenter.department.ilike(f'%{query}%'),
            )
        )
    return q.order_by(CostCenter.code.asc()).paginate(page=page, per_page=per_page, error_out=False)


def list_all_cost_centers():
    return CostCenter.query.filter_by(is_active=True).order_by(CostCenter.name.asc()).all()


def get_cost_center(cost_center_id: int) -> CostCenter:
    return CostCenter.query.get_or_404(cost_center_id)


def create_cost_center(data: dict) -> tuple:
    existing = CostCenter.query.filter_by(code=data['code'].strip().upper()).first()
    if existing:
        return None, 'Já existe um centro de custo com este código.'

    cost_center = CostCenter(
        code=sanitize_text(data['code']).upper(),
        name=sanitize_text(data['name']),
        department=sanitize_text(data.get('department', '')),
        manager=sanitize_text(data.get('manager', '')),
        budget=data.get('budget') or 0,
        description=sanitize_text(data.get('description', '')),
    )
    db.session.add(cost_center)
    db.session.commit()
    log_action('create', 'cost_center', cost_center.id, f'Centro de custo criado: {cost_center.name}')
    return cost_center, None


def update_cost_center(cost_center: CostCenter, data: dict) -> tuple:
    new_code = sanitize_text(data['code']).upper()
    if new_code != cost_center.code:
        existing = CostCenter.query.filter_by(code=new_code).first()
        if existing:
            return None, 'Já existe um centro de custo com este código.'

    cost_center.code = new_code
    cost_center.name = sanitize_text(data['name'])
    cost_center.department = sanitize_text(data.get('department', ''))
    cost_center.manager = sanitize_text(data.get('manager', ''))
    cost_center.budget = data.get('budget') or 0
    cost_center.description = sanitize_text(data.get('description', ''))
    db.session.commit()
    log_action('update', 'cost_center', cost_center.id, f'Centro de custo atualizado: {cost_center.name}')
    return cost_center, None


def delete_cost_center(cost_center: CostCenter) -> tuple:
    if cost_center.payables.count() > 0:
        return False, 'Não é possível excluir um centro de custo com contas a pagar vinculadas. Desative-o ao invés disso.'
    name = cost_center.name
    cost_center_id = cost_center.id
    db.session.delete(cost_center)
    db.session.commit()
    log_action('delete', 'cost_center', cost_center_id, f'Centro de custo excluído: {name}')
    return True, 'Centro de custo excluído com sucesso.'


def toggle_cost_center_status(cost_center: CostCenter) -> CostCenter:
    cost_center.is_active = not cost_center.is_active
    db.session.commit()
    status = 'ativado' if cost_center.is_active else 'desativado'
    log_action('toggle_status', 'cost_center', cost_center.id, f'Centro de custo {status}: {cost_center.name}')
    return cost_center
