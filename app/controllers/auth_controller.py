"""
Controller de autenticação: login, logout, registro, recuperação de senha.
"""

import secrets
from datetime import datetime, timedelta

from flask import current_app, url_for
from flask_login import login_user, logout_user

from app.database.connection import db
from app.models.user import User
from app.services.audit_service import log_action
from app.services.email_service import send_password_reset_email


def authenticate(email: str, password: str) -> tuple:
    """Autentica um usuário. Retorna (user, error_message)."""
    user = User.query.filter_by(email=email.lower().strip()).first()

    if not user:
        return None, 'E-mail ou senha incorretos.'

    if not user.is_active:
        return None, 'Esta conta está desativada. Contate o administrador.'

    if not user.check_password(password):
        return None, 'E-mail ou senha incorretos.'

    return user, None


def perform_login(user: User, remember: bool = False) -> None:
    """Efetua o login do usuário e atualiza o último acesso."""
    login_user(user, remember=remember)
    user.last_login = datetime.utcnow()
    db.session.commit()
    log_action('login', 'user', user.id, f'Login realizado por {user.email}')


def perform_logout(user: User) -> None:
    """Efetua o logout do usuário."""
    if user and user.is_authenticated:
        log_action('logout', 'user', user.id, f'Logout realizado por {user.email}')
    logout_user()


def register_user(name: str, email: str, password: str, role: str = 'viewer') -> tuple:
    """Cria um novo usuário. Retorna (user, error_message)."""
    email = email.lower().strip()
    existing = User.query.filter_by(email=email).first()
    if existing:
        return None, 'Este e-mail já está cadastrado.'

    user = User(name=name.strip(), email=email, role=role, is_active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    log_action('create', 'user', user.id, f'Usuário criado: {email}')
    return user, None


def request_password_reset(email: str) -> bool:
    """Inicia o fluxo de recuperação de senha. Retorna True se e-mail enviado."""
    user = User.query.filter_by(email=email.lower().strip()).first()
    if not user:
        return False

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    reset_url = url_for('auth.reset_password', token=token, _external=True)
    sent = send_password_reset_email(user, reset_url)
    log_action('password_reset_request', 'user', user.id, f'Solicitação de redefinição de senha para {user.email}')
    return sent


def validate_reset_token(token: str) -> User:
    """Valida o token de redefinição de senha e retorna o usuário, se válido."""
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return None
    if not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return None
    return user


def reset_password(user: User, new_password: str) -> None:
    """Define uma nova senha e invalida o token de redefinição."""
    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    log_action('password_reset', 'user', user.id, f'Senha redefinida para {user.email}')


def change_password(user: User, current_password: str, new_password: str) -> tuple:
    """Altera a senha do usuário autenticado. Retorna (sucesso, mensagem)."""
    if not user.check_password(current_password):
        return False, 'A senha atual informada está incorreta.'

    user.set_password(new_password)
    db.session.commit()
    log_action('password_change', 'user', user.id, f'Senha alterada por {user.email}')
    return True, 'Senha alterada com sucesso.'
