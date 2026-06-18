"""
Serviço de auditoria de ações.
"""

from flask import request
from flask_login import current_user
from app.database.connection import db
from app.models.audit_log import AuditLog


def log_action(action: str, entity: str, entity_id: int = None, description: str = None) -> None:
    """Registra uma ação no log de auditoria."""
    try:
        log = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            entity=entity,
            entity_id=entity_id,
            description=description,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:255] if request.user_agent else None,
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
