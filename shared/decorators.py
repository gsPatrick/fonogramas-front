# shared/decorators.py
from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user

def admin_required(f):
    """Decorator para rotas que exigem acesso de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Acesso restrito a administradores.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def usuario_required(f):
    """Decorator para rotas que exigem login (qualquer usuário)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.ativo:
            flash('Sua conta está desativada.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
