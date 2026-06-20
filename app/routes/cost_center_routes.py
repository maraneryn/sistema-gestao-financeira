"""
Rotas de Centro de Custos.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.controllers import cost_center_controller
from app.controllers.forms import CostCenterForm
from app.middlewares.permission_middleware import can_edit_required, can_delete_required

cost_center_bp = Blueprint('cost_center', __name__, template_folder='../templates/cost_centers')


@cost_center_bp.route('/')
@login_required
def index():
    query = request.args.get('query', '').strip() or None
    page = request.args.get('page', 1, type=int)
    pagination = cost_center_controller.list_cost_centers(query=query, page=page)

    return render_template(
        'cost_centers/index.html',
        pagination=pagination,
        items=pagination.items,
        filters={'query': query or ''},
    )


@cost_center_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@can_edit_required
def create():
    form = CostCenterForm()
    if form.validate_on_submit():
        data = {
            'code': form.code.data, 'name': form.name.data, 'department': form.department.data,
            'manager': form.manager.data, 'budget': form.budget.data, 'description': form.description.data,
        }
        cost_center, error = cost_center_controller.create_cost_center(data)
        if error:
            flash(error, 'danger')
        else:
            flash('Centro de custo cadastrado com sucesso!', 'success')
            return redirect(url_for('cost_center.index'))

    return render_template('cost_centers/form.html', form=form, title='Novo Centro de Custo')


@cost_center_bp.route('/<int:cost_center_id>/editar', methods=['GET', 'POST'])
@login_required
@can_edit_required
def edit(cost_center_id):
    cost_center = cost_center_controller.get_cost_center(cost_center_id)
    form = CostCenterForm(obj=cost_center)

    if form.validate_on_submit():
        data = {
            'code': form.code.data, 'name': form.name.data, 'department': form.department.data,
            'manager': form.manager.data, 'budget': form.budget.data, 'description': form.description.data,
        }
        updated, error = cost_center_controller.update_cost_center(cost_center, data)
        if error:
            flash(error, 'danger')
        else:
            flash('Centro de custo atualizado com sucesso!', 'success')
            return redirect(url_for('cost_center.index'))

    return render_template('cost_centers/form.html', form=form, title='Editar Centro de Custo', cost_center=cost_center)


@cost_center_bp.route('/<int:cost_center_id>/alternar-status', methods=['POST'])
@login_required
@can_edit_required
def toggle_status(cost_center_id):
    cost_center = cost_center_controller.get_cost_center(cost_center_id)
    cost_center_controller.toggle_cost_center_status(cost_center)
    flash('Status do centro de custo atualizado.', 'success')
    return redirect(url_for('cost_center.index'))


@cost_center_bp.route('/<int:cost_center_id>/excluir', methods=['POST'])
@login_required
@can_delete_required
def delete(cost_center_id):
    cost_center = cost_center_controller.get_cost_center(cost_center_id)
    success, message = cost_center_controller.delete_cost_center(cost_center)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('cost_center.index'))
