"""
API de Fonogramas - SBACEM
CRUD completo de fonogramas
"""
from flask import request
from flask_login import current_user
from . import api_bp
from .helpers import (
    api_response, api_error, api_paginate,
    require_api_auth, serialize_fonograma
)


@api_bp.route('/fonogramas', methods=['GET'])
@require_api_auth
def listar_fonogramas():
    """
    Listar fonogramas com filtros e paginação
    ---
    tags:
      - Fonogramas
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
        enum: [PENDENTE, ENVIADO, ACEITO, RECUSADO]
      - name: busca
        in: query
        type: string
        description: Busca por ISRC ou título
    responses:
      200:
        description: Lista de fonogramas
      401:
        description: Não autenticado
    """
    from models import db, Fonograma
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    busca = request.args.get('busca', '').strip()
    
    query = Fonograma.query
    
    # Se não for admin, filtrar apenas fonogramas do usuário
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    # Filtros
    if status:
        query = query.filter_by(status_ecad=status)
    
    if busca:
        query = query.filter(
            db.or_(
                Fonograma.isrc.ilike(f'%{busca}%'),
                Fonograma.titulo.ilike(f'%{busca}%')
            )
        )
    
    # Ordenação
    query = query.order_by(Fonograma.created_at.desc())
    
    return api_paginate(
        query, page, per_page,
        lambda f: serialize_fonograma(f, resumido=True)
    )


@api_bp.route('/fonogramas/<int:id>', methods=['GET'])
@require_api_auth
def obter_fonograma(id):
    """
    Obter detalhes de um fonograma
    ---
    tags:
      - Fonogramas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Detalhes do fonograma
      404:
        description: Fonograma não encontrado
    """
    from models import Fonograma
    
    fonograma = Fonograma.query.get(id)
    
    if not fonograma:
        return api_error("Fonograma não encontrado", "NOT_FOUND", status=404)
    
    # Verificar permissão
    if not current_user.is_admin and fonograma.user_id != current_user.id:
        return api_error("Acesso negado", "FORBIDDEN", status=403)
    
    return api_response(data=serialize_fonograma(fonograma))


@api_bp.route('/fonogramas/isrc/<isrc>', methods=['GET'])
@require_api_auth
def obter_fonograma_por_isrc(isrc):
    """
    Obter fonograma por ISRC
    ---
    tags:
      - Fonogramas
    parameters:
      - name: isrc
        in: path
        type: string
        required: true
    responses:
      200:
        description: Detalhes do fonograma
      404:
        description: Fonograma não encontrado
      403:
        description: Acesso negado
    """
    from models import Fonograma
    
    isrc = isrc.strip().upper()
    fonograma = Fonograma.query.filter_by(isrc=isrc).first()
    
    if not fonograma:
        return api_error("Fonograma não encontrado", "NOT_FOUND", status=404)
    
    # Verificar permissão
    if not current_user.is_admin and fonograma.user_id != current_user.id:
        return api_error("Acesso negado", "FORBIDDEN", status=403)
    
    return api_response(data=serialize_fonograma(fonograma))


@api_bp.route('/fonogramas', methods=['POST'])
@require_api_auth
def criar_fonograma():
    """
    Criar novo fonograma
    ---
    tags:
      - Fonogramas
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - isrc
            - titulo
          properties:
            isrc:
              type: string
              example: "BRUM71200729"
            titulo:
              type: string
              example: "Nome da Música"
            duracao:
              type: string
              example: "03:45"
            ano_lanc:
              type: integer
              example: 2024
    responses:
      201:
        description: Fonograma criado
      400:
        description: Dados inválidos
    """
    from models import db, Fonograma
    from shared.validador import validar_isrc
    
    data = request.get_json()
    
    if not data:
        return api_error("Dados não fornecidos", "VALIDATION_ERROR", status=400)
    
    # Validações
    erros = []
    
    isrc = data.get('isrc', '').strip().upper()
    if not isrc:
        erros.append("ISRC é obrigatório")
    elif not validar_isrc(isrc):
        erros.append("ISRC inválido. Formato esperado: BRXXXYYNNNNN")
    elif Fonograma.query.filter_by(isrc=isrc).first():
        erros.append("ISRC já cadastrado no sistema")
    
    titulo = data.get('titulo', '').strip()
    if not titulo:
        erros.append("Título é obrigatório")
    
    if erros:
        return api_error(
            "Validação falhou",
            "VALIDATION_ERROR",
            details=erros,
            status=400
        )
    
    try:
        fonograma = Fonograma(
            isrc=isrc,
            titulo=titulo,
            titulo_obra=data.get('titulo_obra', titulo),
            duracao=data.get('duracao'),
            ano_lanc=data.get('ano_lanc'),
            ano_grav=data.get('ano_grav'),
            genero=data.get('genero'),
            versao=data.get('versao'),
            idioma=data.get('idioma'),
            prod_nome=data.get('prod_nome'),
            prod_doc=data.get('prod_doc'),
            prod_fantasia=data.get('prod_fantasia'),
            prod_perc=data.get('prod_perc'),
            album=data.get('album'),
            selo=data.get('selo'),
            pais=data.get('pais', 'Brasil'),
            formato=data.get('formato'),
            tipo_lanc=data.get('tipo_lanc'),
            status_ecad='PENDENTE',
            user_id=current_user.id
        )
        
        db.session.add(fonograma)
        db.session.commit()
        
        return api_response(
            data={"id": fonograma.id, "isrc": fonograma.isrc},
            message="Fonograma criado com sucesso",
            status=201
        )
        
    except Exception as e:
        db.session.rollback()
        return api_error(
            f"Erro ao criar fonograma: {str(e)}",
            "SERVER_ERROR",
            status=500
        )


@api_bp.route('/fonogramas/<int:id>', methods=['PUT'])
@require_api_auth
def atualizar_fonograma(id):
    """
    Atualizar fonograma existente
    ---
    tags:
      - Fonogramas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            titulo:
              type: string
            duracao:
              type: string
            ano_lanc:
              type: integer
    responses:
      200:
        description: Fonograma atualizado
      404:
        description: Fonograma não encontrado
      403:
        description: Sem permissão para editar
    """
    from models import db, Fonograma
    
    fonograma = Fonograma.query.get(id)
    
    if not fonograma:
        return api_error("Fonograma não encontrado", "NOT_FOUND", status=404)
    
    # Verificar permissão
    if not current_user.is_admin and fonograma.user_id != current_user.id:
        return api_error("Acesso negado", "FORBIDDEN", status=403)
    
    # Verificar se pode editar
    if fonograma.status_ecad in ['ENVIADO', 'ACEITO']:
        return api_error(
            "Fonogramas enviados ou aceitos não podem ser editados",
            "FORBIDDEN",
            status=403
        )
    
    data = request.get_json()
    
    if not data:
        return api_error("Dados não fornecidos", "VALIDATION_ERROR", status=400)
    
    # Campos que podem ser atualizados
    campos_permitidos = [
        'titulo', 'titulo_obra', 'duracao', 'ano_lanc', 'ano_grav',
        'genero', 'versao', 'idioma', 'cod_interno', 'cod_obra',
        'prod_nome', 'prod_doc', 'prod_fantasia', 'prod_perc', 'prod_assoc',
        'album', 'faixa', 'selo', 'formato', 'pais', 'tipo_lanc',
        'situacao', 'territorio', 'prioridade'
    ]
    
    for campo in campos_permitidos:
        if campo in data:
            setattr(fonograma, campo, data[campo])
    
    try:
        db.session.commit()
        return api_response(
            data={"id": fonograma.id},
            message="Fonograma atualizado com sucesso"
        )
    except Exception as e:
        db.session.rollback()
        return api_error(
            f"Erro ao atualizar: {str(e)}",
            "SERVER_ERROR",
            status=500
        )


@api_bp.route('/fonogramas/<int:id>', methods=['DELETE'])
@require_api_auth
def deletar_fonograma(id):
    """
    Deletar fonograma
    ---
    tags:
      - Fonogramas
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Fonograma deletado
      404:
        description: Fonograma não encontrado
      403:
        description: Não é possível deletar
    """
    from models import db, Fonograma
    
    fonograma = Fonograma.query.get(id)
    
    if not fonograma:
        return api_error("Fonograma não encontrado", "NOT_FOUND", status=404)
    
    # Verificar permissão
    if not current_user.is_admin and fonograma.user_id != current_user.id:
        return api_error("Acesso negado", "FORBIDDEN", status=403)
    
    if fonograma.status_ecad in ['ENVIADO', 'ACEITO']:
        return api_error(
            "Fonogramas enviados ou aceitos não podem ser deletados",
            "FORBIDDEN",
            status=403
        )
    
    try:
        db.session.delete(fonograma)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return api_error(
            f"Erro ao deletar: {str(e)}",
            "SERVER_ERROR",
            status=500
        )


@api_bp.route('/fonogramas/stats', methods=['GET'])
@require_api_auth
def stats_fonogramas():
    """
    Estatísticas de fonogramas
    ---
    tags:
      - Fonogramas
    responses:
      200:
        description: Estatísticas
    """
    from models import Fonograma
    
    query = Fonograma.query
    
    # Se não for admin, filtrar apenas fonogramas do usuário
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    total = query.count()
    pendentes = query.filter(
        Fonograma.status_ecad.in_([None, 'PENDENTE', 'NAO_ENVIADO'])
    ).count()
    enviados = query.filter_by(status_ecad='ENVIADO').count()
    aceitos = query.filter_by(status_ecad='ACEITO').count()
    recusados = query.filter_by(status_ecad='RECUSADO').count()
    
    return api_response(data={
        "total": total,
        "pendentes": pendentes,
        "enviados": enviados,
        "aceitos": aceitos,
        "recusados": recusados
    })


@api_bp.route('/fonogramas/buscar', methods=['GET'])
@require_api_auth
def buscar_fonogramas():
    """
    Busca avançada de fonogramas
    ---
    tags:
      - Fonogramas
    parameters:
      - name: q
        in: query
        type: string
        description: Termo de busca
      - name: genero
        in: query
        type: string
      - name: ano_de
        in: query
        type: integer
      - name: ano_ate
        in: query
        type: integer
    responses:
      200:
        description: Resultados da busca
    """
    from models import db, Fonograma
    
    q = request.args.get('q', '').strip()
    genero = request.args.get('genero')
    ano_de = request.args.get('ano_de', type=int)
    ano_ate = request.args.get('ano_ate', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Fonograma.query
    
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    if q:
        query = query.filter(
            db.or_(
                Fonograma.isrc.ilike(f'%{q}%'),
                Fonograma.titulo.ilike(f'%{q}%'),
                Fonograma.prod_nome.ilike(f'%{q}%'),
                Fonograma.album.ilike(f'%{q}%')
            )
        )
    
    if genero:
        query = query.filter_by(genero=genero)
    
    if ano_de:
        query = query.filter(Fonograma.ano_lanc >= ano_de)
    
    if ano_ate:
        query = query.filter(Fonograma.ano_lanc <= ano_ate)
    
    query = query.order_by(Fonograma.created_at.desc())
    
    return api_paginate(
        query, page, per_page,
        lambda f: serialize_fonograma(f, resumido=True)
    )

