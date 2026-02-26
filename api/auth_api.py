"""
API de Autenticação - SBACEM
Endpoints para login, logout e informações do usuário
"""
from flask import request
from flask_login import login_user, logout_user, current_user
from . import api_bp
from .helpers import api_response, api_error, require_api_auth


@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """
    Login via API
    ---
    tags:
      - Autenticação
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: "usuario@email.com"
            password:
              type: string
              example: "senha123"
    responses:
      200:
        description: Login bem sucedido
      401:
        description: Credenciais inválidas
    """
    from models import User
    
    data = request.get_json()
    
    if not data:
        return api_error("Dados não fornecidos", "VALIDATION_ERROR", status=400)
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return api_error(
            "Email e senha são obrigatórios",
            "VALIDATION_ERROR",
            status=400
        )
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return api_error(
            "Email ou senha incorretos",
            "INVALID_CREDENTIALS",
            status=401
        )
    
    if not user.is_active:
        return api_error(
            "Conta desativada. Entre em contato com o administrador.",
            "ACCOUNT_DISABLED",
            status=403
        )
    
    login_user(user)
    
    return api_response(
        data={
            "user": {
                "id": user.id,
                "email": user.email,
                "nome": user.nome,
                "is_admin": user.is_admin
            }
        },
        message="Login realizado com sucesso"
    )


@api_bp.route('/auth/logout', methods=['POST'])
@require_api_auth
def api_logout():
    """
    Logout via API
    ---
    tags:
      - Autenticação
    responses:
      200:
        description: Logout realizado
    """
    logout_user()
    return api_response(message="Logout realizado com sucesso")


@api_bp.route('/auth/me', methods=['GET'])
@require_api_auth
def api_me():
    """
    Dados do usuário logado
    ---
    tags:
      - Autenticação
    responses:
      200:
        description: Dados do usuário
      401:
        description: Não autenticado
    """
    return api_response(
        data={
            "id": current_user.id,
            "email": current_user.email,
            "nome": current_user.nome,
            "is_admin": current_user.is_admin,
            "is_superadmin": current_user.is_admin, # Frontend espera is_superadmin
            "is_active": current_user.is_active
        }
    )


@api_bp.route('/auth/liberar', methods=['POST'])
def api_liberar():
    """
    Handshake SSO do Hub Central via API
    Valida o ticket recebido e inicia sessão local
    """
    import requests
    import os
    from models import User, db
    
    data = request.get_json()
    ticket = data.get('token') or data.get('ticket') # Frontend usa 'token'
    hub_url = os.environ.get('HUB_URL', 'https://api.sbacem.com.br/apicentralizadora')
    system_id = 4 # Fonogramas
    
    if not ticket:
        return api_error("Ticket não fornecido", "VALIDATION_ERROR", status=400)
        
    try:
        # 1. Validar ticket no Hub
        hub_res = requests.post(
            f"{hub_url}/auth/validate-ticket",
            json={"token": ticket, "system_id": system_id},
            timeout=10
        )
        
        if hub_res.status_code != 200:
            return api_error("Ticket inválido no Hub", "INVALID_TICKET", status=401)
            
        hub_data = hub_res.json()
        email = hub_data.get('email')
        # Aceitar tanto is_superadmin quanto is_admin do Hub
        is_admin = hub_data.get('is_superadmin') or hub_data.get('is_admin') or False
        
        # 2. Sincronizar usuário local
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                nome=email.split('@')[0].capitalize(),
                role='admin' if is_admin else 'usuario',
                ativo=True
            )
            import secrets
            user.set_password(secrets.token_hex(16))
            db.session.add(user)
        else:
            user.role = 'admin' if is_admin else 'usuario'
            user.ativo = True
            
        db.session.commit()
        
        # 3. Iniciar sessão Flask-Login
        login_user(user, remember=True)
        
        # 4. Preparar resposta com o cookie específico que o frontend Next.js espera
        hub_jwt = hub_data.get('access_token')
        
        res_data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "nome": user.nome,
                "is_admin": user.is_admin,
                "is_superadmin": user.is_admin
            }
        }
        
        response, status_code = api_response(res_data, message="Handshake realizado com sucesso")
        
        # O cookie satellite_session deve conter o JWT do Hub com prefixo 'token:'
        session_value = f"token:{hub_jwt}" if hub_jwt else f"user:{user.email}"
        
        response.set_cookie(
            'satellite_session',
            session_value,
            httponly=True,
            secure=os.environ.get('FLASK_ENV') == 'production',
            samesite='Lax',
            max_age=3600*24, # 24 horas
            path='/'
        )
        
        return response, status_code
        
    except Exception as e:
        print(f"Erro no handshake SSO API: {str(e)}")
        return api_error(str(e), "SSO_ERROR", status=500)



