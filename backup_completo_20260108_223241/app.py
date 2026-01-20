# app.py - Sistema de Fonogramas SBACEM
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from auth import auth_bp
from admin import admin_bp
from usuario import usuario_bp
import os
import tempfile
from datetime import datetime, timedelta
from sqlalchemy import func

# Configuração
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-dev-123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'fonogramas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Inicializar banco
from models import db, Fonograma, EnvioECAD, RetornoECAD, HistoricoFonograma, User
db.init_app(app)

# Configurar Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para acessar.'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registrar Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp)
app.register_blueprint(usuario_bp)

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('instance', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# ==================== ROTAS WEB ====================

@app.route('/')
def index():
    """Rota inicial: Redireciona para o dashboard apropriado"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('usuario.dashboard'))
    return redirect(url_for('auth.login'))

# ==================== HANDLERS DE ERRO ====================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Recurso não encontrado'}), 404
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
    return render_template('errors/500.html'), 500

# ==================== INICIALIZAÇÃO ====================

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
