"""
Helpers para APIs REST do SBACEM
Funções auxiliares para padronização de respostas
"""
from flask import jsonify
from functools import wraps
from flask_login import current_user


def api_response(data=None, message="Success", status=200, meta=None):
    """
    Resposta padrão de sucesso para APIs
    
    Args:
        data: Dados a retornar
        message: Mensagem de sucesso
        status: Código HTTP (default 200)
        meta: Metadados opcionais (paginação, etc)
    
    Returns:
        Tuple (response, status_code)
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    if meta:
        response["meta"] = meta
    return jsonify(response), status


def api_error(message, code="ERROR", details=None, status=400):
    """
    Resposta padrão de erro para APIs
    
    Args:
        message: Mensagem de erro
        code: Código do erro (ex: VALIDATION_ERROR, NOT_FOUND)
        details: Detalhes adicionais do erro
        status: Código HTTP (default 400)
    
    Returns:
        Tuple (response, status_code)
    """
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    if details:
        response["error"]["details"] = details
    return jsonify(response), status


def api_paginate(query, page, per_page, serialize_func=None):
    """
    Helper para paginação de queries
    
    Args:
        query: SQLAlchemy query object
        page: Número da página
        per_page: Itens por página
        serialize_func: Função para serializar cada item
    
    Returns:
        Tuple (response, status_code)
    """
    # Limitar per_page para evitar sobrecarga
    per_page = min(per_page, 100)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = pagination.items
    if serialize_func:
        items = [serialize_func(item) for item in items]
    
    return api_response(
        data=items,
        meta={
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    )


def require_api_auth(f):
    """
    Decorator para exigir autenticação em endpoints de API
    Retorna 401 se não autenticado
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return api_error(
                "Autenticação necessária",
                "UNAUTHORIZED",
                status=401
            )
        return f(*args, **kwargs)
    return decorated


def require_api_admin(f):
    """
    Decorator para exigir permissão de admin em endpoints de API
    Retorna 401 se não autenticado, 403 se não for admin
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return api_error(
                "Autenticação necessária",
                "UNAUTHORIZED",
                status=401
            )
        if not current_user.is_admin:
            return api_error(
                "Acesso negado. Permissão de administrador necessária.",
                "FORBIDDEN",
                status=403
            )
        return f(*args, **kwargs)
    return decorated


def serialize_fonograma(f, resumido=False):
    """
    Serializa um objeto Fonograma para JSON
    
    Args:
        f: Objeto Fonograma
        resumido: Se True, retorna apenas campos básicos
    
    Returns:
        Dict com dados do fonograma
    """
    if resumido:
        return {
            "id": f.id,
            "isrc": f.isrc,
            "titulo": f.titulo,
            "genero": f.genero,
            "status_ecad": f.status_ecad or "PENDENTE",
            "created_at": f.created_at.isoformat() if f.created_at else None
        }
    
    return {
        "id": f.id,
        "isrc": f.isrc,
        "titulo": f.titulo,
        "titulo_obra": f.titulo_obra,
        "duracao": f.duracao,
        "ano_lanc": f.ano_lanc,
        "ano_grav": f.ano_grav,
        "genero": f.genero,
        "versao": f.versao,
        "idioma": f.idioma,
        "status_ecad": f.status_ecad or "PENDENTE",
        "cod_ecad": f.cod_ecad,
        "cod_interno": f.cod_interno,
        "cod_obra": f.cod_obra,
        
        # Novos campos
        "pais_origem": f.pais_origem,
        "paises_adicionais": f.paises_adicionais,
        "flag_nacional": f.flag_nacional,
        "classificacao_trilha": f.classificacao_trilha,
        "tipo_arranjo": f.tipo_arranjo,
        
        "prod_nome": f.prod_nome,
        "prod_doc": f.prod_doc,
        "prod_fantasia": f.prod_fantasia,
        "prod_perc": f.prod_perc,
        "prod_assoc": f.prod_assoc,
        "album": f.album,
        "faixa": f.faixa,
        "selo": f.selo,
        "formato": f.formato,
        "pais": f.pais,
        "tipo_lanc": f.tipo_lanc,
        "data_lanc": f.data_lanc,
        "situacao": f.situacao,
        "territorio": f.territorio,
        "prioridade": f.prioridade,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "updated_at": f.updated_at.isoformat() if f.updated_at else None
    }

