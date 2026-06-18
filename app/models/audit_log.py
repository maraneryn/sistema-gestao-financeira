"""
Modelo de log de auditoria.
"""

from datetime import datetime
from app.database.connection import db


class AuditLog(db.Model):
    """Registro de auditoria de ações dos usuários."""

    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    entity = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='audit_logs')

    def __repr__(self) -> str:
        return f'<AuditLog {self.action} on {self.entity}>'
