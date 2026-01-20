"""
API ECAD - SBACEM
Endpoints para gerenciar envios e retornos ECAD
"""
from flask import request
from . import api_bp
from .helpers import (
    api_response, api_error, api_paginate,
    require_api_auth, require_api_admin
)


@api_bp.route('/ecad/envios', methods=['GET'])
@require_api_auth
def listar_envios():
    """
    Listar envios ECAD
    ---
    tags:
      - ECAD
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 20
      - name: status
        in: query
        type: string
    responses:
      200:
        description: Lista de envios
    """
    from models import EnvioECAD
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = EnvioECAD.query
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(EnvioECAD.data_envio.desc())
    
    def serialize(e):
        return {
            "id": e.id,
            "protocolo": e.protocolo,
            "data_envio": e.data_envio.isoformat() if e.data_envio else None,
            "tipo_envio": e.tipo_envio,
            "metodo": e.metodo,
            "formato_arquivo": e.formato_arquivo,
            "status": e.status,
            "total_fonogramas": e.total_fonogramas,
            "arquivo_gerado": e.arquivo_gerado
        }
    
    return api_paginate(query, page, per_page, serialize)


@api_bp.route('/ecad/envios/<int:id>', methods=['GET'])
@require_api_auth
def obter_envio(id):
    """
    Obter detalhes de um envio ECAD
    ---
    tags:
      - ECAD
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Detalhes do envio
      404:
        description: Envio não encontrado
    """
    from models import EnvioECAD
    
    envio = EnvioECAD.query.get(id)
    
    if not envio:
        return api_error("Envio não encontrado", "NOT_FOUND", status=404)
    
    # Buscar fonogramas do envio (se houver relacionamento)
    fonogramas = []
    if hasattr(envio, 'fonogramas') and envio.fonogramas:
        fonogramas = [{
            "id": f.id,
            "isrc": f.isrc,
            "titulo": f.titulo,
            "status_ecad": f.status_ecad
        } for f in envio.fonogramas]
    
    return api_response(data={
        "id": envio.id,
        "protocolo": envio.protocolo,
        "data_envio": envio.data_envio.isoformat() if envio.data_envio else None,
        "tipo_envio": envio.tipo_envio,
        "metodo": envio.metodo,
        "formato_arquivo": envio.formato_arquivo,
        "status": envio.status,
        "total_fonogramas": envio.total_fonogramas,
        "arquivo_gerado": envio.arquivo_gerado,
        "observacoes": envio.observacoes,
        "fonogramas": fonogramas
    })


@api_bp.route('/ecad/envios/stats', methods=['GET'])
@require_api_admin
def stats_envios():
    """
    Estatísticas de envios ECAD
    ---
    tags:
      - ECAD
    responses:
      200:
        description: Estatísticas
    """
    from models import EnvioECAD
    from sqlalchemy import func
    
    total = EnvioECAD.query.count()
    
    # Contagem por status
    por_status = {}
    resultados = EnvioECAD.query.with_entities(
        EnvioECAD.status, func.count(EnvioECAD.id)
    ).group_by(EnvioECAD.status).all()
    
    for status, count in resultados:
        por_status[status or 'SEM_STATUS'] = count
    
    # Total de fonogramas enviados
    total_fonogramas = EnvioECAD.query.with_entities(
        func.sum(EnvioECAD.total_fonogramas)
    ).scalar() or 0
    
    return api_response(data={
        "total_envios": total,
        "por_status": por_status,
        "total_fonogramas_enviados": total_fonogramas
    })


@api_bp.route('/ecad/retornos', methods=['GET'])
@require_api_auth
def listar_retornos():
    """
    Listar retornos ECAD
    ---
    tags:
      - ECAD
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 20
    responses:
      200:
        description: Lista de retornos
    """
    from models import RetornoECAD
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = RetornoECAD.query.order_by(RetornoECAD.data_retorno.desc())
    
    def serialize(r):
        return {
            "id": r.id,
            "envio_id": r.envio_id,
            "data_retorno": r.data_retorno.isoformat() if r.data_retorno else None,
            "status_ecad": r.status_ecad,
            "cod_ecad_gerado": r.cod_ecad_gerado,
            "fonograma_id": r.fonograma_id
        }
    
    return api_paginate(query, page, per_page, serialize)


@api_bp.route('/ecad/retornos/<int:id>', methods=['GET'])
@require_api_auth
def obter_retorno(id):
    """
    Obter detalhes de um retorno ECAD
    ---
    tags:
      - ECAD
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Detalhes do retorno
      404:
        description: Retorno não encontrado
    """
    from models import RetornoECAD
    
    retorno = RetornoECAD.query.get(id)
    
    if not retorno:
        return api_error("Retorno não encontrado", "NOT_FOUND", status=404)
    
    return api_response(data={
        "id": retorno.id,
        "envio_id": retorno.envio_id,
        "data_retorno": retorno.data_retorno.isoformat() if retorno.data_retorno else None,
        "status_ecad": retorno.status_ecad,
        "cod_ecad_gerado": retorno.cod_ecad_gerado,
        "codigo_erro": retorno.codigo_erro,
        "mensagem_erro": retorno.mensagem_erro,
        "fonograma_id": retorno.fonograma_id,
        "observacoes": retorno.observacoes
    })

