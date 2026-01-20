# auth/services/email_service.py
"""
Serviço de email para envio de emails transacionais.
Em modo desenvolvimento, imprime no console.
"""

import os
from flask import current_app, url_for

# Configuração de email - será lida de variáveis de ambiente
EMAIL_CONFIG = {
    'MAIL_SERVER': os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
    'MAIL_PORT': int(os.environ.get('MAIL_PORT', 587)),
    'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true',
    'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
    'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD'),
    'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@sbacem.org.br'),
}


def is_dev_mode():
    """Verifica se está em modo desenvolvimento (sem credenciais de email)"""
    return not EMAIL_CONFIG['MAIL_USERNAME'] or not EMAIL_CONFIG['MAIL_PASSWORD']


def enviar_email_recuperacao_senha(usuario, token):
    """
    Envia email de recuperação de senha.
    Em dev mode, imprime no console.
    """
    # Gerar URL de reset
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    assunto = "SBACEM - Recuperação de Senha"
    corpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #22164C 0%, #3D2E6B 50%, #EF234D 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">SBACEM</h1>
            <p style="color: rgba(255,255,255,0.8); margin-top: 5px;">Sistema de Fonogramas</p>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-top: none;">
            <h2 style="color: #333; margin-top: 0;">Recuperação de Senha</h2>
            
            <p style="color: #555;">Olá <strong>{usuario.nome}</strong>,</p>
            
            <p style="color: #555;">Recebemos uma solicitação para redefinir a senha da sua conta. Clique no botão abaixo para criar uma nova senha:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background: linear-gradient(135deg, #22164C, #EF234D); 
                          color: white; 
                          padding: 15px 40px; 
                          text-decoration: none; 
                          border-radius: 8px; 
                          font-weight: bold;
                          display: inline-block;">
                    Redefinir Senha
                </a>
            </div>
            
            <p style="color: #888; font-size: 14px;">
                Se você não solicitou a recuperação de senha, ignore este email. 
                O link expira em <strong>1 hora</strong>.
            </p>
            
            <p style="color: #888; font-size: 14px;">
                Se o botão não funcionar, copie e cole o link abaixo no seu navegador:<br>
                <a href="{reset_url}" style="color: #3D2E6B; word-break: break-all;">{reset_url}</a>
            </p>
        </div>
        
        <div style="background: #22164C; padding: 15px; text-align: center; border-radius: 0 0 10px 10px;">
            <p style="color: rgba(255,255,255,0.6); margin: 0; font-size: 12px;">
                © 2024 SBACEM - Sociedade Brasileira de Autores, Compositores e Escritores de Música
            </p>
        </div>
    </body>
    </html>
    """
    
    corpo_texto = f"""
    SBACEM - Recuperação de Senha
    
    Olá {usuario.nome},
    
    Recebemos uma solicitação para redefinir a senha da sua conta.
    
    Para criar uma nova senha, acesse o link abaixo:
    {reset_url}
    
    Se você não solicitou a recuperação de senha, ignore este email.
    O link expira em 1 hora.
    
    SBACEM - Sistema de Fonogramas
    """
    
    if is_dev_mode():
        # Modo desenvolvimento: imprimir no console
        print("\n" + "=" * 60)
        print("📧 EMAIL DE RECUPERAÇÃO DE SENHA (MODO DEV)")
        print("=" * 60)
        print(f"Para: {usuario.email}")
        print(f"Assunto: {assunto}")
        print("-" * 60)
        print(f"Link de recuperação:")
        print(f">>> {reset_url} <<<")
        print("=" * 60 + "\n")
        return True
    else:
        # Modo produção: enviar email real via SMTP
        return _enviar_email_smtp(
            destinatario=usuario.email,
            assunto=assunto,
            corpo_html=corpo_html,
            corpo_texto=corpo_texto
        )


def _enviar_email_smtp(destinatario, assunto, corpo_html, corpo_texto):
    """Envia email via SMTP"""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From'] = EMAIL_CONFIG['MAIL_DEFAULT_SENDER']
        msg['To'] = destinatario
        
        # Adicionar partes de texto e HTML
        part1 = MIMEText(corpo_texto, 'plain', 'utf-8')
        part2 = MIMEText(corpo_html, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        # Conectar ao servidor SMTP
        server = smtplib.SMTP(EMAIL_CONFIG['MAIL_SERVER'], EMAIL_CONFIG['MAIL_PORT'])
        
        if EMAIL_CONFIG['MAIL_USE_TLS']:
            server.starttls()
        
        server.login(EMAIL_CONFIG['MAIL_USERNAME'], EMAIL_CONFIG['MAIL_PASSWORD'])
        server.sendmail(
            EMAIL_CONFIG['MAIL_DEFAULT_SENDER'],
            destinatario,
            msg.as_string()
        )
        server.quit()
        
        print(f"[EMAIL] Enviado com sucesso para {destinatario}")
        return True
        
    except Exception as e:
        print(f"[EMAIL] Erro ao enviar para {destinatario}: {e}")
        return False
