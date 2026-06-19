"""
Serviço de envio de e-mails (recuperação de senha, notificações).
"""

import logging
from flask import current_app, render_template_string
from flask_mail import Mail, Message

mail = Mail()

logger = logging.getLogger(__name__)

RESET_PASSWORD_TEMPLATE = """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #0d3b66; padding: 24px; text-align: center;">
        <h1 style="color: #ffffff; margin: 0;">{{ company_name }}</h1>
    </div>
    <div style="padding: 24px; background-color: #f5f7fa;">
        <h2 style="color: #0d3b66;">Recuperação de Senha</h2>
        <p>Olá, {{ user_name }}!</p>
        <p>Recebemos uma solicitação para redefinir sua senha. Clique no botão abaixo para criar uma nova senha:</p>
        <p style="text-align: center; margin: 32px 0;">
            <a href="{{ reset_url }}" style="background-color: #0d3b66; color: #ffffff; padding: 12px 24px;
               text-decoration: none; border-radius: 6px; font-weight: bold;">Redefinir Senha</a>
        </p>
        <p>Se você não solicitou essa alteração, ignore este e-mail. O link expira em 1 hora.</p>
        <p style="color: #777777; font-size: 12px;">Este é um e-mail automático, por favor não responda.</p>
    </div>
</div>
"""


def send_password_reset_email(user, reset_url: str) -> bool:
    """Envia e-mail de recuperação de senha. Retorna True se enviado com sucesso."""
    try:
        html_body = render_template_string(
            RESET_PASSWORD_TEMPLATE,
            user_name=user.name,
            reset_url=reset_url,
            company_name=current_app.config.get('COMPANY_NAME', 'Sistema Financeiro'),
        )
        msg = Message(
            subject='Recuperação de Senha - Sistema de Gestão Financeira',
            recipients=[user.email],
            html=html_body,
        )
        mail.send(msg)
        return True
    except Exception as exc:
        logger.warning(f'Falha ao enviar e-mail de recuperação de senha: {exc}')
        return False
