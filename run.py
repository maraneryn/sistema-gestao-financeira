"""
Sistema de Gestão Financeira Empresarial
Entry point da aplicação Flask.
"""

import os
import logging
from app import create_app
from app.database.connection import db
from app.models.user import User
from app.models.category import Category
from app.models.cost_center import CostCenter

app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Disponibiliza objetos no shell Flask."""
    return {
        'db': db,
        'app': app,
        'User': User,
        'Category': Category,
        'CostCenter': CostCenter,
    }


@app.cli.command('init-db')
def init_db():
    """Inicializa o banco de dados com dados padrão."""
    from app.services.seed_service import seed_database
    with app.app_context():
        db.create_all()
        seed_database()
    click_echo('Banco de dados inicializado com sucesso!')


def click_echo(msg):
    import click
    click.echo(msg)


if __name__ == '__main__':
    with app.app_context():
        from app.services.seed_service import seed_database
        db.create_all()
        seed_database()

    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))

    logging.info(f"Iniciando servidor em {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
