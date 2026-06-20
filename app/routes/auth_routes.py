"""
Rotas de autenticação: login, logout, registro, recuperação de senha.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user

from app.controllers.forms import (
    LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm
)
from app.controllers import auth_controller
from app.middlewares.limiter_middleware import limiter

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user, error = auth_controller.authenticate(form.email.data, form.password.data)
        if error:
            flash(error, 'danger')
        else:
            auth_controller.perform_login(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Bem-vindo(a), {user.name}!', 'success')
            return redirect(next_page or url_for('dashboard.index'))

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    auth_controller.perform_logout(current_user)
    flash('Você saiu do sistema com segurança.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/registrar', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user, error = auth_controller.register_user(
            form.name.data, form.email.data, form.password.data, 'viewer'
        )
        if error:
            flash(error, 'danger')
        else:
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        auth_controller.request_password_reset(form.email.data)
        flash('Se o e-mail informado estiver cadastrado, você receberá instruções de recuperação.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    user = auth_controller.validate_reset_token(token)
    if not user:
        flash('Este link de redefinição é inválido ou expirou.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        auth_controller.reset_password(user, form.password.data)
        flash('Senha redefinida com sucesso! Faça login com sua nova senha.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form, token=token)


@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        success, message = auth_controller.change_password(
            current_user, form.current_password.data, form.new_password.data
        )
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/perfil')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)
