"""
Controller de Gestão de Usuários (administração).
"""

from app.database.connection import db
from app.models.user import User
from app.services.audit_service import log_action
from app.services.validators import sanitize_text


def list_users(query: str = None, page: int = 1, per_page: int = 15):
    q = User.query
    if query:
        q = q.filter(
            db.or_(
                User.name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%'),
            )
        )
    return q.order_by(User.name.asc()).paginate(page=page, per_page=per_page, error_out=False)


def get_user(user_id: int) -> User:
    return User.query.get_or_404(user_id)


def create_user(data: dict) -> tuple:
    email = data['email'].lower().strip()
    existing = User.query.filter_by(email=email).first()
    if existing:
        return None, 'Este e-mail já está cadastrado.'

    user = User(
        name=sanitize_text(data['name']),
        email=email,
        role=data.get('role', 'viewer'),
        is_active=data.get('is_active', True),
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    log_action('create', 'user', user.id, f'Usuário criado: {user.email}')
    return user, None


def update_user(user: User, data: dict, editor) -> tuple:
    new_email = data['email'].lower().strip()
    if new_email != user.email:
        existing = User.query.filter_by(email=new_email).first()
        if existing:
            return None, 'Este e-mail já está em uso por outro usuário.'

    if user.id == editor.id and data.get('role') != user.role:
        return None, 'Você não pode alterar seu próprio perfil de acesso.'

    user.name = sanitize_text(data['name'])
    user.email = new_email
    user.role = data.get('role', user.role)
    user.is_active = data.get('is_active', user.is_active)

    if data.get('password'):
        user.set_password(data['password'])

    db.session.commit()
    log_action('update', 'user', user.id, f'Usuário atualizado: {user.email}')
    return user, None


def delete_user(user: User, requester) -> tuple:
    if user.id == requester.id:
        return False, 'Você não pode excluir sua própria conta.'

    email = user.email
    user_id = user.id
    db.session.delete(user)
    db.session.commit()
    log_action('delete', 'user', user_id, f'Usuário excluído: {email}')
    return True, 'Usuário excluído com sucesso.'


def toggle_user_status(user: User, requester) -> tuple:
    if user.id == requester.id:
        return None, 'Você não pode desativar sua própria conta.'

    user.is_active = not user.is_active
    db.session.commit()
    status = 'ativado' if user.is_active else 'desativado'
    log_action('toggle_status', 'user', user.id, f'Usuário {status}: {user.email}')
    return user, None
