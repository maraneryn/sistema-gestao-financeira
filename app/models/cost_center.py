"""
Modelo de centro de custos.
"""

from datetime import datetime
from app.database.connection import db


class CostCenter(db.Model):
    """Centro de custos para agrupamento por departamento."""

    __tablename__ = 'cost_centers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    manager = db.Column(db.String(120), nullable=True)
    budget = db.Column(db.Numeric(15, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payables = db.relationship('Payable', backref='cost_center', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<CostCenter {self.code} - {self.name}>'
