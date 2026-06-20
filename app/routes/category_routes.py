"""
Rotas de Categorias Financeiras.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.controllers import category_controller
from app.controllers.forms import CategoryForm
from app.middlewares.permission_middleware import can_edit_required, can_delete_required

category_bp = Blueprint('category', __name__, template_folder='../templates/categories')


@category_bp.route('/')
@login_required
def index():
    query = request.args.get('query', '').strip() or None
    type_filter = request.args.get('type', '').strip() or None
    page = request.args.get('page', 1, type=int)
    pagination = category_controller.list_categories(query=query, type_filter=type_filter, page=page)

    return render_template(
        'categories/index.html',
        pagination=pagination,
        items=pagination.items,
        filters={'query': query or '', 'type': type_filter or ''},
    )


@category_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@can_edit_required
def create():
    form = CategoryForm()
    if form.validate_on_submit():
        data = {
            'name': form.name.data, 'type': form.type.data, 'description': form.description.data,
            'color': form.color.data, 'icon': form.icon.data,
        }
        category_controller.create_category(data)
        flash('Categoria cadastrada com sucesso!', 'success')
        return redirect(url_for('category.index'))

    return render_template('categories/form.html', form=form, title='Nova Categoria')


@category_bp.route('/<int:category_id>/editar', methods=['GET', 'POST'])
@login_required
@can_edit_required
def edit(category_id):
    category = category_controller.get_category(category_id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        data = {
            'name': form.name.data, 'type': form.type.data, 'description': form.description.data,
            'color': form.color.data, 'icon': form.icon.data,
        }
        category_controller.update_category(category, data)
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('category.index'))

    return render_template('categories/form.html', form=form, title='Editar Categoria', category=category)


@category_bp.route('/<int:category_id>/alternar-status', methods=['POST'])
@login_required
@can_edit_required
def toggle_status(category_id):
    category = category_controller.get_category(category_id)
    category_controller.toggle_category_status(category)
    flash('Status da categoria atualizado.', 'success')
    return redirect(url_for('category.index'))


@category_bp.route('/<int:category_id>/excluir', methods=['POST'])
@login_required
@can_delete_required
def delete(category_id):
    category = category_controller.get_category(category_id)
    success, message = category_controller.delete_category(category)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('category.index'))
