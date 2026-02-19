from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from models import User, db
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('usuario.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user is None or not user.check_password(password):
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.ativo:
            flash('Sua conta está desativada.', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.is_admin:
                next_page = url_for('admin.dashboard')
            else:
                next_page = url_for('usuario.dashboard')
                
        return redirect(next_page)
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('usuario.dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        associacao = request.form.get('associacao')
        
        if password != confirm:
            flash('As senhas não conferem.', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            nome=nome,
            email=email,
            role='usuario',
            associacao=associacao,
            ativo=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/liberar')
def liberar():
    """Handshake SSO do Hub Central"""
    token = request.args.get('token')
    if not token:
        return redirect(url_for('auth.login'))
    
    # Renderizar página de loading premium
    return render_template('auth/liberar.html', ticket=token)

@auth_bp.route('/validate-ticket', methods=['POST'])
def validate_ticket():
    """Valida o ticket recebido do Hub e inicia sessão local"""
    import requests
    import os
    
    data = request.get_json()
    ticket = data.get('ticket')
    hub_url = os.environ.get('HUB_URL', 'https://api.sbacem.com.br/apicentralizadora')
    system_id = 4 # Fonogramas
    
    try:
        # 1. Validar ticket no Hub
        hub_res = requests.post(
            f"{hub_url}/auth/validate-ticket",
            json={"token": ticket, "system_id": system_id},
            timeout=10
        )
        
        if hub_res.status_code != 200:
            return jsonify({"success": False, "error": "Ticket inválido"}), 401
            
        hub_data = hub_res.json()
        email = hub_data.get('email')
        is_admin = hub_data.get('is_superadmin', False)
        
        # 2. Sincronizar usuário local
        user = User.query.filter_by(email=email).first()
        if not user:
            # Criar usuário se não existir (vindo do Hub)
            user = User(
                email=email,
                nome=email.split('@')[0].capitalize(),
                role='admin' if is_admin else 'usuario',
                ativo=True
            )
            # Senha aleatória para usuários SSO
            import secrets
            user.set_password(secrets.token_hex(16))
            db.session.add(user)
        else:
            # Atualizar role se mudou no Hub
            user.role = 'admin' if is_admin else 'usuario'
            user.ativo = True
            
        db.session.commit()
        
        # 3. Iniciar sessão
        login_user(user, remember=True)
        
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Erro no handshake SSO: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== RECUPERAÇÃO DE SENHA ====================

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Solicitar recuperação de senha"""
    if current_user.is_authenticated:
        return redirect(url_for('usuario.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Por favor, informe seu email.', 'warning')
            return redirect(url_for('auth.forgot_password'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.ativo:
            # Gerar token e enviar email
            from auth.services.email_service import enviar_email_recuperacao_senha
            
            token = user.generate_reset_token()
            db.session.commit()
            
            enviar_email_recuperacao_senha(user, token)
        
        # Mensagem genérica por segurança (não revelar se email existe)
        flash('Se o email estiver cadastrado, você receberá um link para redefinir sua senha.', 'info')
        
        return redirect(url_for('auth.forgot_password'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Redefinir senha com token"""
    if current_user.is_authenticated:
        return redirect(url_for('usuario.dashboard'))
    
    # Buscar usuário pelo token
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token():
        flash('Link de recuperação inválido ou expirado.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if not password or len(password) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'warning')
            return redirect(url_for('auth.reset_password', token=token))
        
        if password != confirm:
            flash('As senhas não conferem.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
        
        # Atualizar senha e limpar token
        user.set_password(password)
        user.clear_reset_token()
        db.session.commit()
        
        flash('Senha redefinida com sucesso! Faça login com sua nova senha.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token, email=user.email)
