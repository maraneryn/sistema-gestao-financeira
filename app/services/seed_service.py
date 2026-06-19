"""
Serviço de carga inicial (seed) do banco de dados.
Cria usuário administrador padrão e categorias/centros de custo básicos
caso ainda não existam, de forma idempotente.
"""

import os
from app.database.connection import db
from app.models.user import User
from app.models.category import Category
from app.models.cost_center import CostCenter


def seed_database() -> None:
    """Popula o banco com dados essenciais, sem duplicar registros."""
    _seed_admin_user()
    _seed_categories()
    _seed_cost_centers()
    db.session.commit()


def _seed_admin_user() -> None:
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@empresa.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin@123456')

    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        return

    admin = User(
        name='Administrador',
        email=admin_email,
        role='admin',
        is_active=True,
    )
    admin.set_password(admin_password)
    db.session.add(admin)


def _seed_categories() -> None:
    if Category.query.count() > 0:
        return

    default_categories = [
        ('Vendas de Produtos', 'receita', '#198754', 'bi-graph-up-arrow'),
        ('Prestação de Serviços', 'receita', '#20c997', 'bi-briefcase'),
        ('Outras Receitas', 'receita', '#0dcaf0', 'bi-cash-coin'),
        ('Aluguel', 'despesa_fixa', '#dc3545', 'bi-building'),
        ('Folha de Pagamento', 'despesa_fixa', '#fd7e14', 'bi-people'),
        ('Internet e Telefonia', 'despesa_fixa', '#6f42c1', 'bi-wifi'),
        ('Materiais de Escritório', 'despesa_variavel', '#d63384', 'bi-pencil'),
        ('Marketing e Publicidade', 'despesa_variavel', '#ffc107', 'bi-megaphone'),
        ('Manutenção', 'despesa_variavel', '#6c757d', 'bi-tools'),
        ('ICMS', 'imposto', '#212529', 'bi-receipt'),
        ('ISS', 'imposto', '#343a40', 'bi-receipt-cutoff'),
        ('Simples Nacional', 'imposto', '#495057', 'bi-file-earmark-text'),
        ('Equipamentos', 'investimento', '#0d6efd', 'bi-pc-display'),
        ('Tecnologia', 'investimento', '#6610f2', 'bi-cpu'),
        ('Outros', 'outro', '#adb5bd', 'bi-three-dots'),
    ]

    for name, type_, color, icon in default_categories:
        db.session.add(Category(name=name, type=type_, color=color, icon=icon))


def _seed_cost_centers() -> None:
    if CostCenter.query.count() > 0:
        return

    default_centers = [
        ('ADM', 'Administrativo', 'Administração'),
        ('COM', 'Comercial', 'Vendas'),
        ('FIN', 'Financeiro', 'Financeiro'),
        ('TI', 'Tecnologia da Informação', 'TI'),
        ('OPE', 'Operações', 'Operacional'),
    ]

    for code, name, department in default_centers:
        db.session.add(CostCenter(code=code, name=name, department=department))
