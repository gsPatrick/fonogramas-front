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
            "is_active": current_user.is_active
        }
    )



