"""
Rotas de Gestão de Usuários (administração de acesso).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.controllers import user_controller
from app.controllers.forms import UserForm
from app.middlewares.permission_middleware import admin_required

user_bp = Blueprint('user', __name__, template_folder='../templates/users')


@user_bp.route('/')
@login_required
@admin_required
def index():
    query = request.args.get('query', '').strip() or None
    page = request.args.get('page', 1, type=int)
    pagination = user_controller.list_users(query=query, page=page)

    return render_template(
        'users/index.html',
        pagination=pagination,
        items=pagination.items,
        filters={'query': query or ''},
    )


@user_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        if not form.password.data:
            form.password.errors.append('A senha é obrigatória para novos usuários.')
        else:
            data = {
                'name': form.name.data, 'email': form.email.data, 'role': form.role.data,
                'is_active': form.is_active.data, 'password': form.password.data,
            }
            user, error = user_controller.create_user(data)
            if error:
                flash(error, 'danger')
            else:
                flash('Usuário cadastrado com sucesso!', 'success')
                return redirect(url_for('user.index'))

    return render_template('users/form.html', form=form, title='Novo Usuário')


@user_bp.route('/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    user = user_controller.get_user(user_id)
    form = UserForm(obj=user)
    form.password.data = ''

    if form.validate_on_submit():
        data = {
            'name': form.name.data, 'email': form.email.data, 'role': form.role.data,
            'is_active': form.is_active.data, 'password': form.password.data,
        }
        updated, error = user_controller.update_user(user, data, current_user)
        if error:
            flash(error, 'danger')
        else:
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('user.index'))

    return render_template('users/form.html', form=form, title='Editar Usuário', user=user)


@user_bp.route('/<int:user_id>/alternar-status', methods=['POST'])
@login_required
@admin_required
def toggle_status(user_id):
    user = user_controller.get_user(user_id)
    updated, error = user_controller.toggle_user_status(user, current_user)
    if error:
        flash(error, 'danger')
    else:
        flash('Status do usuário atualizado.', 'success')
    return redirect(url_for('user.index'))


@user_bp.route('/<int:user_id>/excluir', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    user = user_controller.get_user(user_id)
    success, message = user_controller.delete_user(user, current_user)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('user.index'))
