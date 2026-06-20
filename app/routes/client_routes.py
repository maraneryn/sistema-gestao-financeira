"""
Rotas de Gestão de Clientes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.controllers import client_controller
from app.controllers.forms import ClientForm
from app.middlewares.permission_middleware import can_edit_required, can_delete_required
from app.models.receivable import Receivable

client_bp = Blueprint('client', __name__, template_folder='../templates/clients')


@client_bp.route('/')
@login_required
def index():
    query = request.args.get('query', '').strip() or None
    page = request.args.get('page', 1, type=int)
    pagination = client_controller.list_clients(query=query, page=page)

    return render_template(
        'clients/index.html',
        pagination=pagination,
        items=pagination.items,
        filters={'query': query or ''},
    )


@client_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@can_edit_required
def create():
    form = ClientForm()
    if form.validate_on_submit():
        data = {
            'name': form.name.data, 'document': form.document.data, 'document_type': form.document_type.data,
            'email': form.email.data, 'phone': form.phone.data, 'address': form.address.data,
            'city': form.city.data, 'state': form.state.data, 'zip_code': form.zip_code.data,
            'notes': form.notes.data,
        }
        client_controller.create_client(data)
        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('client.index'))

    return render_template('clients/form.html', form=form, title='Novo Cliente')


@client_bp.route('/<int:client_id>/editar', methods=['GET', 'POST'])
@login_required
@can_edit_required
def edit(client_id):
    client = client_controller.get_client(client_id)
    form = ClientForm(obj=client)

    if form.validate_on_submit():
        data = {
            'name': form.name.data, 'document': form.document.data, 'document_type': form.document_type.data,
            'email': form.email.data, 'phone': form.phone.data, 'address': form.address.data,
            'city': form.city.data, 'state': form.state.data, 'zip_code': form.zip_code.data,
            'notes': form.notes.data,
        }
        client_controller.update_client(client, data)
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('client.index'))

    return render_template('clients/form.html', form=form, title='Editar Cliente', client=client)


@client_bp.route('/<int:client_id>')
@login_required
def view(client_id):
    client = client_controller.get_client(client_id)
    receivables = client.receivables.order_by(Receivable.due_date.desc()).all()
    return render_template('clients/view.html', client=client, receivables=receivables)


@client_bp.route('/<int:client_id>/alternar-status', methods=['POST'])
@login_required
@can_edit_required
def toggle_status(client_id):
    client = client_controller.get_client(client_id)
    client_controller.toggle_client_status(client)
    flash('Status do cliente atualizado.', 'success')
    return redirect(url_for('client.index'))


@client_bp.route('/<int:client_id>/excluir', methods=['POST'])
@login_required
@can_delete_required
def delete(client_id):
    client = client_controller.get_client(client_id)
    success, message = client_controller.delete_client(client)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('client.index'))
