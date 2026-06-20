"""
Rotas de Gestão de Fornecedores.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.controllers import supplier_controller
from app.controllers.forms import SupplierForm
from app.middlewares.permission_middleware import can_edit_required, can_delete_required
from app.models.payable import Payable

supplier_bp = Blueprint('supplier', __name__, template_folder='../templates/suppliers')


@supplier_bp.route('/')
@login_required
def index():
    query = request.args.get('query', '').strip() or None
    page = request.args.get('page', 1, type=int)
    pagination = supplier_controller.list_suppliers(query=query, page=page)

    return render_template(
        'suppliers/index.html',
        pagination=pagination,
        items=pagination.items,
        filters={'query': query or ''},
    )


@supplier_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@can_edit_required
def create():
    form = SupplierForm()
    if form.validate_on_submit():
        data = {
            'name': form.name.data, 'document': form.document.data, 'document_type': form.document_type.data,
            'email': form.email.data, 'phone': form.phone.data, 'address': form.address.data,
            'city': form.city.data, 'state': form.state.data, 'zip_code': form.zip_code.data,
            'notes': form.notes.data,
        }
        supplier_controller.create_supplier(data)
        flash('Fornecedor cadastrado com sucesso!', 'success')
        return redirect(url_for('supplier.index'))

    return render_template('suppliers/form.html', form=form, title='Novo Fornecedor')


@supplier_bp.route('/<int:supplier_id>/editar', methods=['GET', 'POST'])
@login_required
@can_edit_required
def edit(supplier_id):
    supplier = supplier_controller.get_supplier(supplier_id)
    form = SupplierForm(obj=supplier)

    if form.validate_on_submit():
        data = {
            'name': form.name.data, 'document': form.document.data, 'document_type': form.document_type.data,
            'email': form.email.data, 'phone': form.phone.data, 'address': form.address.data,
            'city': form.city.data, 'state': form.state.data, 'zip_code': form.zip_code.data,
            'notes': form.notes.data,
        }
        supplier_controller.update_supplier(supplier, data)
        flash('Fornecedor atualizado com sucesso!', 'success')
        return redirect(url_for('supplier.index'))

    return render_template('suppliers/form.html', form=form, title='Editar Fornecedor', supplier=supplier)


@supplier_bp.route('/<int:supplier_id>')
@login_required
def view(supplier_id):
    supplier = supplier_controller.get_supplier(supplier_id)
    payables = supplier.payables.order_by(Payable.due_date.desc()).all()
    return render_template('suppliers/view.html', supplier=supplier, payables=payables)


@supplier_bp.route('/<int:supplier_id>/alternar-status', methods=['POST'])
@login_required
@can_edit_required
def toggle_status(supplier_id):
    supplier = supplier_controller.get_supplier(supplier_id)
    supplier_controller.toggle_supplier_status(supplier)
    flash('Status do fornecedor atualizado.', 'success')
    return redirect(url_for('supplier.index'))


@supplier_bp.route('/<int:supplier_id>/excluir', methods=['POST'])
@login_required
@can_delete_required
def delete(supplier_id):
    supplier = supplier_controller.get_supplier(supplier_id)
    success, message = supplier_controller.delete_supplier(supplier)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('supplier.index'))
