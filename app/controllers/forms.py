"""
Formulários da aplicação com validação via Flask-WTF / WTForms.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, DecimalField,
    DateField, TextAreaField, BooleanField, HiddenField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Optional, NumberRange, ValidationError
)

from app.services.validators import validate_document


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(message='Informe o e-mail.'), Email(message='E-mail inválido.')])
    password = PasswordField('Senha', validators=[DataRequired(message='Informe a senha.')])
    remember = BooleanField('Manter conectado')


class RegisterForm(FlaskForm):
    name = StringField('Nome completo', validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8, message='A senha deve ter ao menos 8 caracteres.')])
    confirm_password = PasswordField(
        'Confirmar senha',
        validators=[DataRequired(), EqualTo('password', message='As senhas não coincidem.')]
    )
    role = SelectField('Perfil de acesso', choices=[
        ('viewer', 'Visualizador'),
        ('operator', 'Operador'),
        ('manager', 'Gerente'),
        ('admin', 'Administrador'),
    ])

    def validate_password(self, field):
        import re
        value = field.data
        if not re.search(r'[A-Z]', value) or not re.search(r'[a-z]', value) or not re.search(r'\d', value):
            raise ValidationError('A senha deve conter letras maiúsculas, minúsculas e números.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova senha', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirmar nova senha',
        validators=[DataRequired(), EqualTo('password', message='As senhas não coincidem.')]
    )


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Senha atual', validators=[DataRequired()])
    new_password = PasswordField('Nova senha', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirmar nova senha',
        validators=[DataRequired(), EqualTo('new_password', message='As senhas não coincidem.')]
    )


# ---------------------------------------------------------------------------
# Contas a Receber / Pagar
# ---------------------------------------------------------------------------

class ReceivableForm(FlaskForm):
    description = StringField('Descrição', validators=[DataRequired(), Length(max=255)])
    amount = DecimalField('Valor', validators=[DataRequired(), NumberRange(min=0.01, message='O valor deve ser maior que zero.')], places=2)
    due_date = DateField('Data de vencimento', validators=[DataRequired()])
    client_id = SelectField('Cliente', coerce=int, validators=[Optional()])
    category_id = SelectField('Categoria', coerce=int, validators=[Optional()])
    invoice_number = StringField('Número da nota/fatura', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Observações', validators=[Optional(), Length(max=2000)])


class ReceivableReceiveForm(FlaskForm):
    received_amount = DecimalField('Valor recebido', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    received_date = DateField('Data do recebimento', validators=[DataRequired()])


class PayableForm(FlaskForm):
    description = StringField('Descrição', validators=[DataRequired(), Length(max=255)])
    amount = DecimalField('Valor', validators=[DataRequired(), NumberRange(min=0.01, message='O valor deve ser maior que zero.')], places=2)
    due_date = DateField('Data de vencimento', validators=[DataRequired()])
    supplier_id = SelectField('Fornecedor', coerce=int, validators=[Optional()])
    category_id = SelectField('Categoria', coerce=int, validators=[Optional()])
    cost_center_id = SelectField('Centro de custo', coerce=int, validators=[Optional()])
    invoice_number = StringField('Número da nota/fatura', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Observações', validators=[Optional(), Length(max=2000)])


class PayablePayForm(FlaskForm):
    paid_amount = DecimalField('Valor pago', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    paid_date = DateField('Data do pagamento', validators=[DataRequired()])


# ---------------------------------------------------------------------------
# Cadastros
# ---------------------------------------------------------------------------

class ClientForm(FlaskForm):
    name = StringField('Nome / Razão Social', validators=[DataRequired(), Length(max=150)])
    document_type = SelectField('Tipo de documento', choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')])
    document = StringField('CPF/CNPJ', validators=[Optional(), Length(max=20)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=255)])
    phone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    address = StringField('Endereço', validators=[Optional(), Length(max=255)])
    city = StringField('Cidade', validators=[Optional(), Length(max=100)])
    state = StringField('UF', validators=[Optional(), Length(max=2)])
    zip_code = StringField('CEP', validators=[Optional(), Length(max=10)])
    notes = TextAreaField('Observações', validators=[Optional(), Length(max=2000)])

    def validate_document(self, field):
        if field.data and not validate_document(field.data, self.document_type.data):
            raise ValidationError(f'{self.document_type.data} inválido.')


class SupplierForm(FlaskForm):
    name = StringField('Nome / Razão Social', validators=[DataRequired(), Length(max=150)])
    document_type = SelectField('Tipo de documento', choices=[('CNPJ', 'CNPJ'), ('CPF', 'CPF')])
    document = StringField('CPF/CNPJ', validators=[Optional(), Length(max=20)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=255)])
    phone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    address = StringField('Endereço', validators=[Optional(), Length(max=255)])
    city = StringField('Cidade', validators=[Optional(), Length(max=100)])
    state = StringField('UF', validators=[Optional(), Length(max=2)])
    zip_code = StringField('CEP', validators=[Optional(), Length(max=10)])
    notes = TextAreaField('Observações', validators=[Optional(), Length(max=2000)])

    def validate_document(self, field):
        if field.data and not validate_document(field.data, self.document_type.data):
            raise ValidationError(f'{self.document_type.data} inválido.')


class CategoryForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    type = SelectField('Tipo', choices=[
        ('receita', 'Receita'),
        ('despesa_fixa', 'Despesa Fixa'),
        ('despesa_variavel', 'Despesa Variável'),
        ('imposto', 'Imposto'),
        ('investimento', 'Investimento'),
        ('outro', 'Outro'),
    ])
    description = StringField('Descrição', validators=[Optional(), Length(max=255)])
    color = StringField('Cor', validators=[Optional(), Length(max=7)], default='#007bff')
    icon = StringField('Ícone', validators=[Optional(), Length(max=50)], default='bi-tag')


class CostCenterForm(FlaskForm):
    code = StringField('Código', validators=[DataRequired(), Length(max=20)])
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    department = StringField('Departamento', validators=[Optional(), Length(max=100)])
    manager = StringField('Responsável', validators=[Optional(), Length(max=120)])
    budget = DecimalField('Orçamento', validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=255)])


class UserForm(FlaskForm):
    name = StringField('Nome completo', validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=255)])
    role = SelectField('Perfil de acesso', choices=[
        ('viewer', 'Visualizador'),
        ('operator', 'Operador'),
        ('manager', 'Gerente'),
        ('admin', 'Administrador'),
    ])
    is_active = BooleanField('Usuário ativo', default=True)
    password = PasswordField('Senha', validators=[Optional(), Length(min=8)])


class SearchForm(FlaskForm):
    """Formulário genérico de pesquisa/filtro (CSRF desabilitado pois usa GET)."""
    class Meta:
        csrf = False

    query = StringField('Pesquisar', validators=[Optional(), Length(max=255)])
    date_start = DateField('Data inicial', validators=[Optional()])
    date_end = DateField('Data final', validators=[Optional()])
    category_id = SelectField('Categoria', coerce=int, validators=[Optional()])
    status = SelectField('Situação', validators=[Optional()])
