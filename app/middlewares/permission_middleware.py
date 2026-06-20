"""
Middleware de controle de permissões por perfil de acesso (RBAC).
"""

from functools import wraps
from flask import abort
from flask_login import current_user


def roles_required(*roles):
    """Decorator que restringe o acesso a usuários com determinados perfis."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if not current_user.has_role(*roles):
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def can_edit_required(view_func):
    """Decorator que exige permissão de edição (admin, manager, operator)."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_edit():
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


def can_delete_required(view_func):
    """Decorator que exige permissão de exclusão (admin, manager)."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_delete():
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


def admin_required(view_func):
    """Decorator que exige perfil de administrador."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped
