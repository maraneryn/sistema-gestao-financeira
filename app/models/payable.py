"""
Modelo de contas a pagar.
"""

from datetime import datetime, date
from app.database.connection import db


class Payable(db.Model):
    """Contas a pagar da empresa."""

    __tablename__ = 'payables'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date, nullable=True)
    paid_amount = db.Column(db.Numeric(15, 2), nullable=True)
    status = db.Column(db.String(20), default='pendente', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    invoice_number = db.Column(db.String(50), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    cost_center_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUS_OPTIONS = {
        'pendente': 'Pendente',
        'pago': 'Pago',
        'vencido': 'Vencido',
        'cancelado': 'Cancelado',
        'parcial': 'Parcialmente Pago',
    }

    @property
    def status_label(self) -> str:
        return self.STATUS_OPTIONS.get(self.status, self.status)

    @property
    def is_overdue(self) -> bool:
        return self.status == 'pendente' and self.due_date < date.today()

    @property
    def days_overdue(self) -> int:
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0

    def mark_as_paid(self, paid_amount=None, paid_date=None) -> None:
        self.paid_date = paid_date or date.today()
        self.paid_amount = paid_amount or self.amount
        if self.paid_amount >= self.amount:
            self.status = 'pago'
        else:
            self.status = 'parcial'

    def __repr__(self) -> str:
        return f'<Payable {self.description} - R${self.amount}>'
