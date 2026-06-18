"""
Modelo de usuário do sistema.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.connection import db


class User(UserMixin, db.Model):
    """Modelo de usuário com controle de acesso por perfil."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ROLES = {
        'admin': 'Administrador',
        'manager': 'Gerente',
        'operator': 'Operador',
        'viewer': 'Visualizador',
    }

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_role(self, *roles: str) -> bool:
        return self.role in roles

    def can_edit(self) -> bool:
        return self.role in ('admin', 'manager', 'operator')

    def can_delete(self) -> bool:
        return self.role in ('admin', 'manager')

    def is_admin(self) -> bool:
        return self.role == 'admin'

    @property
    def role_label(self) -> str:
        return self.ROLES.get(self.role, self.role)

    def __repr__(self) -> str:
        return f'<User {self.email}>'
