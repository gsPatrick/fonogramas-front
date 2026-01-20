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
