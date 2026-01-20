"""
API de Relatórios - SBACEM
Endpoints para estatísticas e relatórios
"""
from flask import request
from flask_login import current_user
from . import api_bp
from .helpers import api_response, api_error, require_api_auth, require_api_admin


@api_bp.route('/relatorios/dashboard', methods=['GET'])
@require_api_auth
def dashboard_stats():
    """
    Dados do dashboard
    ---
    tags:
      - Relatórios
    responses:
      200:
        description: Estatísticas do dashboard
    """
    from models import Fonograma, EnvioECAD
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Base query
    query = Fonograma.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    # Contagens básicas
    total = query.count()
    pendentes = query.filter(
        Fonograma.status_ecad.in_([None, 'PENDENTE', 'NAO_ENVIADO'])
    ).count()
    enviados = query.filter_by(status_ecad='ENVIADO').count()
    aceitos = query.filter_by(status_ecad='ACEITO').count()
    recusados = query.filter_by(status_ecad='RECUSADO').count()
    
    # Últimos 30 dias
    data_30_dias = datetime.now() - timedelta(days=30)
    novos_30_dias = query.filter(Fonograma.created_at >= data_30_dias).count()
    
    # Taxa de aprovação
    total_processados = aceitos + recusados
    taxa_aprovacao = round((aceitos / total_processados * 100), 1) if total_processados > 0 else 0
    
    return api_response(data={
        "fonogramas": {
            "total": total,
            "pendentes": pendentes,
            "enviados": enviados,
            "aceitos": aceitos,
            "recusados": recusados,
            "novos_30_dias": novos_30_dias
        },
        "metricas": {
            "taxa_aprovacao": taxa_aprovacao
        }
    })


@api_bp.route('/relatorios/por-genero', methods=['GET'])
@require_api_auth
def relatorio_por_genero():
    """
    Distribuição de fonogramas por gênero
    ---
    tags:
      - Relatórios
    responses:
      200:
        description: Distribuição por gênero
    """
    from models import db, Fonograma
    from sqlalchemy import func
    
    query = Fonograma.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    resultados = query.with_entities(
        Fonograma.genero, func.count(Fonograma.id)
    ).group_by(Fonograma.genero).all()
    
    dados = []
    for genero, count in resultados:
        dados.append({
            "genero": genero or "Não informado",
            "quantidade": count
        })
    
    # Ordenar por quantidade
    dados.sort(key=lambda x: x['quantidade'], reverse=True)
    
    return api_response(data=dados)


@api_bp.route('/relatorios/por-status', methods=['GET'])
@require_api_auth
def relatorio_por_status():
    """
    Distribuição de fonogramas por status ECAD
    ---
    tags:
      - Relatórios
    responses:
      200:
        description: Distribuição por status
    """
    from models import db, Fonograma
    from sqlalchemy import func
    
    query = Fonograma.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    resultados = query.with_entities(
        Fonograma.status_ecad, func.count(Fonograma.id)
    ).group_by(Fonograma.status_ecad).all()
    
    dados = []
    for status, count in resultados:
        dados.append({
            "status": status or "PENDENTE",
            "quantidade": count
        })
    
    return api_response(data=dados)


@api_bp.route('/relatorios/por-ano', methods=['GET'])
@require_api_auth
def relatorio_por_ano():
    """
    Distribuição de fonogramas por ano de lançamento
    ---
    tags:
      - Relatórios
    responses:
      200:
        description: Distribuição por ano
    """
    from models import db, Fonograma
    from sqlalchemy import func
    
    query = Fonograma.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    resultados = query.with_entities(
        Fonograma.ano_lanc, func.count(Fonograma.id)
    ).filter(Fonograma.ano_lanc.isnot(None)
    ).group_by(Fonograma.ano_lanc
    ).order_by(Fonograma.ano_lanc.desc()
    ).limit(20).all()
    
    dados = []
    for ano, count in resultados:
        dados.append({
            "ano": ano,
            "quantidade": count
        })
    
    return api_response(data=dados)


@api_bp.route('/relatorios/evolucao-mensal', methods=['GET'])
@require_api_auth
def evolucao_mensal():
    """
    Evolução mensal de cadastros (últimos 12 meses)
    ---
    tags:
      - Relatórios
    responses:
      200:
        description: Evolução mensal
    """
    from models import db, Fonograma
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    
    # Últimos 12 meses
    data_inicio = datetime.now() - timedelta(days=365)
    
    query = Fonograma.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    resultados = query.filter(
        Fonograma.created_at >= data_inicio
    ).with_entities(
        extract('year', Fonograma.created_at).label('ano'),
        extract('month', Fonograma.created_at).label('mes'),
        func.count(Fonograma.id)
    ).group_by('ano', 'mes'
    ).order_by('ano', 'mes').all()
    
    dados = []
    for ano, mes, count in resultados:
        dados.append({
            "ano": int(ano),
            "mes": int(mes),
            "periodo": f"{int(mes):02d}/{int(ano)}",
            "quantidade": count
        })
    
    return api_response(data=dados)


@api_bp.route('/admin/stats', methods=['GET'])
@require_api_admin
def admin_stats():
    """
    Estatísticas administrativas
    ---
    tags:
      - Admin
    responses:
      200:
        description: Estatísticas administrativas
    """
    from models import User, Fonograma, EnvioECAD
    
    total_usuarios = User.query.count()
    usuarios_ativos = User.query.filter_by(is_active=True).count()
    total_fonogramas = Fonograma.query.count()
    total_envios = EnvioECAD.query.count()
    
    return api_response(data={
        "usuarios": {
            "total": total_usuarios,
            "ativos": usuarios_ativos
        },
        "fonogramas": {
            "total": total_fonogramas
        },
        "envios": {
            "total": total_envios
        }
    })


@api_bp.route('/admin/usuarios', methods=['GET'])
@require_api_admin
def listar_usuarios():
    """
    Listar usuários (admin only)
    ---
    tags:
      - Admin
    responses:
      200:
        description: Lista de usuários
    """
    from models import User
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = User.query.order_by(User.created_at.desc())
    
    def serialize(u):
        return {
            "id": u.id,
            "email": u.email,
            "nome": u.nome,
            "is_admin": u.is_admin,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
    
    from .helpers import api_paginate
    return api_paginate(query, page, per_page, serialize)



