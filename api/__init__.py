"""
Módulo de APIs REST do SBACEM
Prefixo: /api/

Estrutura:
- /api/health          - Health check
- /api/auth/*          - Autenticação
- /api/fonogramas/*    - CRUD de fonogramas
- /api/validar/*       - Validação de dados
- /api/ecad/*          - Envios e retornos ECAD
- /api/relatorios/*    - Estatísticas e relatórios
"""
from flask import Blueprint

# Blueprint principal da API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Health check básico
@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check da API
    ---
    tags:
      - Sistema
    responses:
      200:
        description: API está funcionando
    """
    from .helpers import api_response
    return api_response(
        data={"status": "healthy", "service": "SBACEM API"},
        message="API está funcionando"
    )


@api_bp.route('/status', methods=['GET'])
def api_status():
    """
    Status detalhado da API
    ---
    tags:
      - Sistema
    responses:
      200:
        description: Status da API com informações do sistema
    """
    from .helpers import api_response
    from datetime import datetime
    
    return api_response(
        data={
            "status": "online",
            "service": "SBACEM - Sistema de Fonogramas",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    )


# Importar sub-módulos de API
from . import auth_api
from . import fonogramas_api
from . import validacao_api
from . import ecad_api
from . import relatorios_api



