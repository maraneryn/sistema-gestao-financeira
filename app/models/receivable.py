"""
Modelo de contas a receber.
"""

from datetime import datetime, date
from app.database.connection import db


class Receivable(db.Model):
    """Contas a receber da empresa."""

    __tablename__ = 'receivables'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    received_date = db.Column(db.Date, nullable=True)
    received_amount = db.Column(db.Numeric(15, 2), nullable=True)
    status = db.Column(db.String(20), default='pendente', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    invoice_number = db.Column(db.String(50), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUS_OPTIONS = {
        'pendente': 'Pendente',
        'recebido': 'Recebido',
        'vencido': 'Vencido',
        'cancelado': 'Cancelado',
        'parcial': 'Parcialmente Recebido',
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

    def mark_as_received(self, received_amount=None, received_date=None) -> None:
        self.received_date = received_date or date.today()
        self.received_amount = received_amount or self.amount
        if self.received_amount >= self.amount:
            self.status = 'recebido'
        else:
            self.status = 'parcial'

    def __repr__(self) -> str:
        return f'<Receivable {self.description} - R${self.amount}>'
