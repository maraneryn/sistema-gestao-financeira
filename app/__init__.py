"""
Fábrica da aplicação Flask - Sistema de Gestão Financeira Empresarial.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template

from app.config.settings import config_map
from app.database.connection import db, migrate
from app.middlewares.auth_middleware import login_manager
from app.middlewares.csrf_middleware import csrf
from app.middlewares.limiter_middleware import limiter


def create_app(env_name: str = 'development') -> Flask:
    """Cria e configura a instância da aplicação Flask."""
    app = Flask(__name__, template_folder='templates', static_folder='static')

    config_class = config_map.get(env_name, config_map['development'])
    app.config.from_object(config_class)

    _init_extensions(app)
    _init_logging(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_context_processors(app)
    _register_health_check(app)

    return app


def _init_extensions(app: Flask) -> None:
    """Inicializa todas as extensões Flask."""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)


def _init_logging(app: Flask) -> None:
    """Configura o sistema de logging da aplicação."""
    os.makedirs('logs', exist_ok=True)

    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    file_handler = RotatingFileHandler(
        app.config.get('LOG_FILE', 'logs/app.log'),
        maxBytes=10_485_760,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    if not app.debug:
        app.logger.info('Sistema de Gestão Financeira iniciado.')


def _register_blueprints(app: Flask) -> None:
    """Registra todos os blueprints da aplicação."""
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.cashflow_routes import cashflow_bp
    from app.routes.receivable_routes import receivable_bp
    from app.routes.payable_routes import payable_bp
    from app.routes.cost_center_routes import cost_center_bp
    from app.routes.category_routes import category_bp
    from app.routes.client_routes import client_bp
    from app.routes.supplier_routes import supplier_bp
    from app.routes.report_routes import report_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(cashflow_bp, url_prefix='/fluxo-caixa')
    app.register_blueprint(receivable_bp, url_prefix='/contas-receber')
    app.register_blueprint(payable_bp, url_prefix='/contas-pagar')
    app.register_blueprint(cost_center_bp, url_prefix='/centros-custo')
    app.register_blueprint(category_bp, url_prefix='/categorias')
    app.register_blueprint(client_bp, url_prefix='/clientes')
    app.register_blueprint(supplier_bp, url_prefix='/fornecedores')
    app.register_blueprint(report_bp, url_prefix='/relatorios')
    app.register_blueprint(user_bp, url_prefix='/usuarios')


def _register_error_handlers(app: Flask) -> None:
    """Registra os handlers de erro HTTP."""

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        app.logger.error(f'Erro interno: {e}')
        return render_template('errors/500.html'), 500


def _register_context_processors(app: Flask) -> None:
    """Registra context processors globais."""
    from datetime import datetime

    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.now(),
            'app_name': app.config.get('APP_NAME', 'FinanceiroERP'),
            'company_name': app.config.get('COMPANY_NAME', 'Minha Empresa'),
        }


def _register_health_check(app: Flask) -> None:
    """Registra endpoint de health check."""

    @app.route('/health')
    def health():
        from flask import jsonify
        return jsonify({'status': 'healthy', 'version': '1.0.0'})
