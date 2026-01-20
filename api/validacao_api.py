"""
API de Validação - SBACEM
Endpoints para validar ISRC, CPF, CNPJ e outros dados
"""
from flask import request
from . import api_bp
from .helpers import api_response, api_error


@api_bp.route('/validar/isrc', methods=['POST'])
def validar_isrc_api():
    """
    Validar código ISRC
    ---
    tags:
      - Validação
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            isrc:
              type: string
              example: "BRUM71200729"
    responses:
      200:
        description: Resultado da validação
    """
    from shared.validador import validar_isrc
    
    data = request.get_json()
    isrc = data.get('isrc', '') if data else ''
    
    isrc = isrc.strip().upper()
    valido = validar_isrc(isrc)
    
    # Verificar se já existe no banco
    existe = False
    if valido:
        from models import Fonograma
        existe = Fonograma.query.filter_by(isrc=isrc).first() is not None
    
    return api_response(data={
        "isrc": isrc,
        "valido": valido,
        "existe_no_sistema": existe,
        "mensagem": "ISRC válido" if valido else "ISRC inválido. Formato: BRXXXYYNNNNN"
    })


@api_bp.route('/validar/cpf', methods=['POST'])
def validar_cpf_api():
    """
    Validar CPF
    ---
    tags:
      - Validação
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            cpf:
              type: string
              example: "529.982.247-25"
    responses:
      200:
        description: Resultado da validação
    """
    from shared.validador import validar_cpf
    
    data = request.get_json()
    cpf = data.get('cpf', '') if data else ''
    
    valido = validar_cpf(cpf)
    
    # Formatar CPF se válido
    cpf_formatado = None
    if valido:
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    
    return api_response(data={
        "cpf": cpf,
        "cpf_formatado": cpf_formatado,
        "valido": valido,
        "mensagem": "CPF válido" if valido else "CPF inválido"
    })


@api_bp.route('/validar/cnpj', methods=['POST'])
def validar_cnpj_api():
    """
    Validar CNPJ
    ---
    tags:
      - Validação
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            cnpj:
              type: string
              example: "11.222.333/0001-81"
    responses:
      200:
        description: Resultado da validação
    """
    from shared.validador import validar_cnpj
    
    data = request.get_json()
    cnpj = data.get('cnpj', '') if data else ''
    
    valido = validar_cnpj(cnpj)
    
    # Formatar CNPJ se válido
    cnpj_formatado = None
    if valido:
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    
    return api_response(data={
        "cnpj": cnpj,
        "cnpj_formatado": cnpj_formatado,
        "valido": valido,
        "mensagem": "CNPJ válido" if valido else "CNPJ inválido"
    })


@api_bp.route('/validar/documento', methods=['POST'])
def validar_documento_api():
    """
    Validar CPF ou CNPJ automaticamente
    ---
    tags:
      - Validação
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            documento:
              type: string
              example: "529.982.247-25"
    responses:
      200:
        description: Resultado da validação
    """
    from shared.validador import validar_cpf, validar_cnpj
    
    data = request.get_json()
    doc = data.get('documento', '') if data else ''
    
    # Remover formatação
    doc_limpo = ''.join(filter(str.isdigit, doc))
    
    if len(doc_limpo) == 11:
        tipo = "CPF"
        valido = validar_cpf(doc)
    elif len(doc_limpo) == 14:
        tipo = "CNPJ"
        valido = validar_cnpj(doc)
    else:
        return api_response(data={
            "documento": doc,
            "tipo": None,
            "valido": False,
            "mensagem": "Documento deve ter 11 dígitos (CPF) ou 14 dígitos (CNPJ)"
        })
    
    return api_response(data={
        "documento": doc,
        "tipo": tipo,
        "valido": valido,
        "mensagem": f"{tipo} {'válido' if valido else 'inválido'}"
    })


@api_bp.route('/validar/duracao', methods=['POST'])
def validar_duracao_api():
    """
    Validar e formatar duração
    ---
    tags:
      - Validação
    parameters:
      - name: body
        in: body
        schema:
          type: object
          properties:
            duracao:
              type: string
              example: "3:45"
    responses:
      200:
        description: Resultado da validação
    """
    import re
    
    data = request.get_json()
    duracao = data.get('duracao', '') if data else ''
    
    # Aceita formatos: "3:45", "03:45", "3.45", "225" (segundos)
    duracao = duracao.strip()
    
    # Tentar parsear
    minutos = 0
    segundos = 0
    valido = False
    formatado = None
    
    # Formato MM:SS ou M:SS
    match = re.match(r'^(\d{1,2}):(\d{2})$', duracao)
    if match:
        minutos = int(match.group(1))
        segundos = int(match.group(2))
        valido = segundos < 60
    
    # Formato MM.SS
    if not valido:
        match = re.match(r'^(\d{1,2})\.(\d{2})$', duracao)
        if match:
            minutos = int(match.group(1))
            segundos = int(match.group(2))
            valido = segundos < 60
    
    # Apenas segundos totais
    if not valido and duracao.isdigit():
        total_seg = int(duracao)
        minutos = total_seg // 60
        segundos = total_seg % 60
        valido = True
    
    if valido:
        formatado = f"{minutos:02d}:{segundos:02d}"
        total_segundos = minutos * 60 + segundos
    else:
        total_segundos = None
    
    return api_response(data={
        "duracao_original": duracao,
        "duracao_formatada": formatado,
        "total_segundos": total_segundos,
        "valido": valido,
        "mensagem": "Duração válida" if valido else "Formato inválido. Use MM:SS"
    })



