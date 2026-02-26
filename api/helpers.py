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
        "updated_at": f.updated_at.isoformat() if f.updated_at else None,
        
        # Listas de Participantes
        "autores": [
            {
                "nome": a.nome,
                "cpf": a.cpf,
                "funcao": a.funcao,
                "percentual": a.percentual,
                "cae_ipi": a.cae_ipi,
                "data_nascimento": a.data_nascimento.isoformat() if a.data_nascimento else None,
                "nacionalidade": a.nacionalidade
            } for a in f.autores_list
        ],
        "interpretes": [
            {
                "nome": i.nome,
                "doc": i.doc,
                "categoria": i.categoria,
                "percentual": i.percentual,
                "associacao": i.associacao,
                "cae_ipi": i.cae_ipi,
                "data_nascimento": i.data_nascimento.isoformat() if i.data_nascimento else None,
                "nacionalidade": i.nacionalidade
            } for i in f.interpretes_list
        ],
        "musicos": [
            {
                "nome": m.nome,
                "cpf": m.cpf,
                "instrumento": m.instrumento,
                "tipo": m.tipo,
                "percentual": m.percentual
            } for m in f.musicos_list
        ],
        "editoras": [
            {
                "nome": e.nome,
                "cnpj": e.cnpj,
                "percentual": e.percentual,
                "nacionalidade": e.nacionalidade
            } for e in f.editoras_list
        ]
    }

def gerar_pdf_proposta(proposta, output_path):
    """
    Gera um PDF da proposta de filiação.
    """
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Cabeçalho
    pdf.cell(190, 10, "SBACEM - PROPOSTA DE FILIAÇÃO", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 10, f"Protocolo: {proposta.protocolo}", ln=True, align="C")
    pdf.ln(10)
    
    # Dados Pessoais
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Dados Pessoais", ln=True, fill=False)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 6, f"Nome Completo: {proposta.nome_completo}", ln=True)
    pdf.cell(190, 6, f"CPF: {proposta.cpf}", ln=True)
    pdf.cell(190, 6, f"E-mail: {proposta.email}", ln=True)
    pdf.cell(190, 6, f"Celular: {proposta.celular}", ln=True)
    pdf.cell(190, 6, f"Data de Nascimento: {proposta.data_nascimento}", ln=True)
    pdf.ln(5)
    
    # Endereço
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Endereço", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 6, f"Logradouro: {proposta.rua}, {proposta.numero}", ln=True)
    pdf.cell(190, 6, f"Bairro: {proposta.bairro}", ln=True)
    pdf.cell(190, 6, f"Cidade/UF: {proposta.cidade}/{proposta.uf}", ln=True)
    pdf.cell(190, 6, f"CEP: {proposta.cep}", ln=True)
    pdf.ln(5)
    
    # Dados Bancários
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Dados Bancários", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 6, f"Banco: {proposta.banco}", ln=True)
    pdf.cell(190, 6, f"Agência: {proposta.agencia} | Conta: {proposta.conta} ({proposta.tipo_conta})", ln=True)
    pdf.ln(10)
    
    # Rodapé / Espaço para assinatura (opcional, já que é digital)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(190, 10, "Este documento foi gerado eletronicamente e passará por assinatura digital via Clicksign.", ln=True, align="C")
    
    pdf.output(output_path)
    return output_path

