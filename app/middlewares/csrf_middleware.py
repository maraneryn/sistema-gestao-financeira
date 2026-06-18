"""
Middleware de proteção CSRF.
"""

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
