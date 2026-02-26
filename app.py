# app.py - Sistema de Fonogramas SBACEM
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_cors import CORS
from flasgger import Swagger
from flask_wtf.csrf import CSRFProtect
from auth import auth_bp
from admin import admin_bp
from usuario import usuario_bp
from api import api_bp  # API REST
import os
from dotenv import load_dotenv
import tempfile
import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from functools import wraps
import time

# Carregar variáveis de ambiente
load_dotenv()

# ==================== CONFIGURAÇÃO ====================
app = Flask(__name__)

# Detectar ambiente
PRODUCTION = os.environ.get('FLASK_ENV', 'development') == 'production'

# Configurações básicas
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-dev-123-TROCAR-EM-PRODUCAO')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'fonogramas.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Configurações de sessão segura
app.config['SESSION_COOKIE_SECURE'] = PRODUCTION  # HTTPS only em produção
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Previne XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Proteção CSRF
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# CSRF Protection
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hora

# ==================== LOGGING ====================
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO if PRODUCTION else logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== INICIALIZAÇÃO SEGURANÇA ====================
csrf = CSRFProtect(app)

# Isentar rotas de API do CSRF (usam autenticação própria)
@csrf.exempt
def csrf_exempt_api():
    pass

# ==================== RATE LIMITING (Simples) ====================
request_counts = {}
RATE_LIMIT = 100  # requests por minuto
RATE_WINDOW = 60  # segundos

def get_client_ip():
    """Obtém IP real do cliente (considera proxy)"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

@app.before_request
def auto_login_from_satellite_cookie():
    """Realiza login automático se houver um cookie satellite_session válido"""
    if not current_user.is_authenticated:
        token = request.cookies.get('satellite_session')
        if token and token.startswith('token:'):
            from jose import jwt
            from models import User, db
            
            jwt_token = token.split(':', 1)[1]
            # Chave do Hub Centralizada encontrada no VPS
            HUB_SECRET_KEY = os.environ.get('HUB_SECRET_KEY', 'prod_secret_key_bf3c8592_change_me_to_something_very_secure_in_real_prod')
            HUB_ALGORITHM = 'HS256'
            
            try:
                payload = jwt.decode(jwt_token, HUB_SECRET_KEY, algorithms=[HUB_ALGORITHM])
                email = payload.get('sub')
                if email:
                    user = User.query.filter_by(email=email).first()
                    if user and user.is_active:
                        # Sincronizar permissão de admin vinda do token
                        is_admin = payload.get('is_superadmin', False)
                        user.role = 'admin' if is_admin else 'usuario'
                        db.session.commit()
                        
                        login_user(user, remember=True)
                        app.logger.info(f"Auto-login via satellite_session para {email} (admin={is_admin})")
            except Exception as e:
                # Token inválido ou expirado - silencioso
                pass

@app.before_request
def rate_limit():
    """Rate limiting simples baseado em IP"""
    # Não aplicar a arquivos estáticos
    if request.path.startswith('/static'):
        return None
    
    client_ip = get_client_ip()
    current_time = time.time()
    
    # Limpar entradas antigas
    if client_ip in request_counts:
        request_counts[client_ip] = [
            t for t in request_counts[client_ip] 
            if current_time - t < RATE_WINDOW
        ]
    else:
        request_counts[client_ip] = []
    
    # Verificar limite
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        logger.warning(f"Rate limit excedido para IP: {client_ip}")
        return jsonify({'error': 'Muitas requisições. Tente novamente em 1 minuto.'}), 429
    
    request_counts[client_ip].append(current_time)

# ==================== SECURITY HEADERS ====================
@app.after_request
def add_security_headers(response):
    """Adiciona headers de segurança em todas as respostas"""
    # Previne XSS
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy (relaxado para permitir CDNs)
    if not request.path.startswith('/api/docs'):  # Swagger precisa de inline scripts
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: blob:; "
        )
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

# ==================== SWAGGER CONFIG ====================
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: '/api/' in rule.rule,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "SBACEM API",
        "description": "API REST do Sistema de Fonogramas SBACEM",
        "version": "1.0.0",
        "contact": {
            "name": "SBACEM",
            "email": "contato@sbacem.org.br"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "cookieAuth": {
            "type": "apiKey",
            "name": "session",
            "in": "cookie",
            "description": "Session cookie (login via /api/auth/login)"
        }
    },
    "tags": [
        {"name": "Sistema", "description": "Health check e status"},
        {"name": "Autenticação", "description": "Login e logout"},
        {"name": "Fonogramas", "description": "CRUD de fonogramas"},
        {"name": "Validação", "description": "Validação de dados (ISRC, CPF, CNPJ)"},
        {"name": "ECAD", "description": "Envios e retornos ECAD"},
        {"name": "Relatórios", "description": "Estatísticas e relatórios"},
        {"name": "Admin", "description": "Funções administrativas"}
    ]
}

# ==================== CORS CONFIG ====================
# Permite requisições de sistemas externos (Java, etc)
# Em produção, definir CORS_ORIGINS com origens permitidas separadas por vírgula
# Exemplo: CORS_ORIGINS=http://intranet.empresa.com,https://app.empresa.com
cors_origins = os.environ.get('CORS_ORIGINS', '*')
cors_origins_list = [o.strip() for o in cors_origins.split(',')] if cors_origins != '*' else ["*"]

cors_config = {
    r"/api/*": {
        "origins": cors_origins_list,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    },
    r"/public/*": {
        "origins": cors_origins_list,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "x-draft-token"],
        "supports_credentials": True
    }
}

# Inicializar banco
from models import db, Fonograma, EnvioECAD, RetornoECAD, HistoricoFonograma, User
db.init_app(app)

# Inicializar CORS e Swagger
CORS(app, resources=cors_config)
swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Configurar Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para acessar.'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ENDPOINTS ADICIONAIS NEXT.JS ====================

@app.route('/api/auth/me', methods=['GET'])
@csrf.exempt
def get_me():
    """Retorna dados do usuário logado para o Next.js AuthGuard"""
    if not current_user.is_authenticated:
        return jsonify({"success": False, "error": "Não autenticado"}), 401
    return jsonify({
        "success": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "nome": current_user.nome,
            "role": current_user.role,
            "is_admin": current_user.is_admin
        }
    })

@app.route('/api/lote/validar', methods=['POST'])
@csrf.exempt
def api_lote_validar():
    """Validação instantânea de arquivo para o Grid do Next.js"""
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    arquivo = request.files['file']
    from shared.processador import processar_csv
    import tempfile
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(arquivo.filename)[1]) as tmp:
        arquivo.save(tmp.name)
        try:
            df, erros, encoding, delim = processar_csv(tmp.name)
            # Converter DataFrame para lista de dicts para o grid
            dados = df.to_dict('records')
            return jsonify({
                "success": True,
                "data": dados,
                "errors": erros,
                "total": len(dados)
            })
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('instance', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# ==================== HEALTH CHECK ====================
@app.route('/health')
def health_check():
    """Endpoint de health check para monitoramento"""
    try:
        # Testa conexão com banco
        db.session.execute(db.text('SELECT 1'))
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy' if db_status == 'ok' else 'unhealthy',
        'database': db_status,
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200 if db_status == 'ok' else 500

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
