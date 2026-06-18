"""
Modelo de fornecedores.
"""

from datetime import datetime
from app.database.connection import db


class Supplier(db.Model):
    """Fornecedores da empresa."""

    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    document = db.Column(db.String(20), nullable=True)
    document_type = db.Column(db.String(10), default='CNPJ')
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(2), nullable=True)
    zip_code = db.Column(db.String(10), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payables = db.relationship('Payable', backref='supplier', lazy='dynamic')

    @property
    def total_payable(self):
        from app.models.payable import Payable
        from sqlalchemy import func
        result = db.session.query(func.sum(Payable.amount)).filter(
            Payable.supplier_id == self.id,
            Payable.status == 'pendente'
        ).scalar()
        return result or 0.00

    def __repr__(self) -> str:
        return f'<Supplier {self.name}>'
