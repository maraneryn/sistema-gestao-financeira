"""
Modelo de categorias financeiras.
"""

from datetime import datetime
from app.database.connection import db


class Category(db.Model):
    """Categorias para classificação de transações financeiras."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    color = db.Column(db.String(7), default='#007bff')
    icon = db.Column(db.String(50), default='bi-tag')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    TYPES = {
        'receita': 'Receita',
        'despesa_fixa': 'Despesa Fixa',
        'despesa_variavel': 'Despesa Variável',
        'imposto': 'Imposto',
        'investimento': 'Investimento',
        'outro': 'Outro',
    }

    receivables = db.relationship('Receivable', backref='category', lazy='dynamic')
    payables = db.relationship('Payable', backref='category', lazy='dynamic')

    @property
    def type_label(self) -> str:
        return self.TYPES.get(self.type, self.type)

    def __repr__(self) -> str:
        return f'<Category {self.name}>'
