"""
Serviço para operações CRUD de fonogramas
"""

import pandas as pd
from models import db, Fonograma, Autor, Editora, Interprete, Musico, Documento
from .processador import parse_autores, parse_interpretes, parse_musicos, parse_editoras, parse_documentos
from .validador import limpar_documento
from typing import Dict


def safe_str(value, default=''):
    """Converte valor para string de forma segura, tratando None, NaN, int, float"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    return str(value).strip()

def safe_int(value, default=None):
    """Converte valor para int de forma segura"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    try:
        s = str(value).strip()
        if not s or s.lower() == 'nan':
            return default
        return int(float(s))  # float first to handle "2024.0"
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """Converte valor para float de forma segura"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    try:
        s = str(value).strip().replace('%', '').replace(',', '.')
        if not s or s.lower() == 'nan':
            return default
        return float(s)
    except (ValueError, TypeError):
        return default


def criar_fonograma_do_dataframe(row: Dict) -> Fonograma:
    """Cria um fonograma a partir de uma linha do DataFrame"""
    fonograma = Fonograma(
        isrc=safe_str(row.get('isrc')),
        titulo=safe_str(row.get('titulo')),
        versao=safe_str(row.get('versao')) or None,
        duracao=safe_str(row.get('duracao')),
        ano_grav=safe_int(row.get('ano_grav')),
        ano_lanc=safe_int(row.get('ano_lanc')) or safe_int(row.get('ano_grav')) or 2024,  # Garantir valor não-nulo
        idioma=safe_str(row.get('idioma')) or None,
        genero=safe_str(row.get('genero')),
        cod_interno=safe_str(row.get('cod_interno')) or None,
        titulo_obra=safe_str(row.get('titulo_obra')),
        cod_obra=safe_str(row.get('cod_obra')) or None,
        # Novos campos
        pais_origem=safe_str(row.get('pais_origem')) or None,
        paises_adicionais=safe_str(row.get('paises_adicionais')) or None,
        flag_nacional=safe_str(row.get('flag_nacional')) or None,
        classificacao_trilha=safe_str(row.get('classificacao_trilha')) or None,
        tipo_arranjo=safe_str(row.get('tipo_arranjo')) or None,
        subdivisao_estrangeiro=safe_str(row.get('subdivisao_estrangeiro')) or None,
        publicacao_simultanea=bool(row.get('publicacao_simultanea')) if row.get('publicacao_simultanea') else False,
        
        prod_nome=safe_str(row.get('prod_nome')),
        prod_doc=limpar_documento(safe_str(row.get('prod_doc'))),
        prod_fantasia=safe_str(row.get('prod_fantasia')) or None,
        prod_endereco=safe_str(row.get('prod_endereco')) or None,
        prod_perc=safe_float(row.get('prod_perc')),
        prod_assoc=safe_str(row.get('prod_assoc')) or None,
        prod_data_ini=safe_str(row.get('prod_data_ini')) or None,
        tipo_lanc=safe_str(row.get('tipo_lanc')) or None,
        album=safe_str(row.get('album')) or None,
        faixa=safe_int(row.get('faixa')),
        selo=safe_str(row.get('selo')) or None,
        formato=safe_str(row.get('formato')) or None,
        pais=safe_str(row.get('pais')) or None,
        data_lanc=safe_str(row.get('data_lanc')) or None,
        assoc_gestao=safe_str(row.get('assoc_gestao')) or None,
        data_cad=safe_str(row.get('data_cad')) or None,
        situacao=safe_str(row.get('situacao')) or 'ATIVO',
        obs_juridicas=safe_str(row.get('obs_juridicas')) or None,
        historico=safe_str(row.get('historico')) or None,
        territorio=safe_str(row.get('territorio')) or None,
        tipos_exec=safe_str(row.get('tipos_exec')) or None,
        prioridade=safe_str(row.get('prioridade')) or None,
        cod_ecad=safe_str(row.get('cod_ecad')) or None,
    )
    
    # Adiciona autores
    autores_input = row.get('autores')
    if isinstance(autores_input, list):
        autores_data = autores_input
    else:
        autores_data = parse_autores(autores_input or '')
    for autor_data in autores_data:
        autor = Autor(
            nome=autor_data['nome'],
            cpf=autor_data['cpf'],
            funcao=autor_data['funcao'],
            percentual=autor_data['percentual'],
            cae_ipi=autor_data.get('cae_ipi') or None,
            data_nascimento=autor_data.get('data_nascimento') or None,
            nacionalidade=autor_data.get('nacionalidade') or None
        )
        fonograma.autores_list.append(autor)
    
    # Adiciona editoras
    editoras_input = row.get('editoras')
    if isinstance(editoras_input, list):
        editoras_data = editoras_input
    else:
        editoras_data = parse_editoras(editoras_input or '')
    for editora_data in editoras_data:
        editora = Editora(
            nome=editora_data['nome'],
            cnpj=editora_data['cnpj'],
            percentual=editora_data['percentual'],
            nacionalidade=editora_data.get('nacionalidade') or None
        )
        fonograma.editoras_list.append(editora)
    
    # Adiciona intérpretes
    interpretes_input = row.get('interpretes')
    if isinstance(interpretes_input, list):
        interpretes_data = interpretes_input
    else:
        interpretes_data = parse_interpretes(interpretes_input or '')
    for interprete_data in interpretes_data:
        interprete = Interprete(
            nome=interprete_data['nome'],
            doc=interprete_data['doc'],
            categoria=interprete_data['categoria'],
            percentual=interprete_data['percentual'],
            associacao=interprete_data.get('associacao', '') or None,
            cae_ipi=interprete_data.get('cae_ipi') or None,
            data_nascimento=interprete_data.get('data_nascimento') or None,
            nacionalidade=interprete_data.get('nacionalidade') or None
        )
        fonograma.interpretes_list.append(interprete)
    
    # Adiciona músicos
    musicos_input = row.get('musicos')
    if isinstance(musicos_input, list):
        musicos_data = musicos_input
    else:
        musicos_data = parse_musicos(musicos_input or '')
    for musico_data in musicos_data:
        musico = Musico(
            nome=musico_data['nome'],
            cpf=musico_data['cpf'],
            instrumento=musico_data['instrumento'],
            tipo=musico_data['tipo'],
            percentual=musico_data['percentual']
        )
        fonograma.musicos_list.append(musico)
    
    # Adiciona documentos
    documentos_input = row.get('documentos')
    if isinstance(documentos_input, list):
        documentos_data = documentos_input
    else:
        documentos_data = parse_documentos(documentos_input or '')
    for documento_data in documentos_data:
        documento = Documento(
            tipo=documento_data['tipo'],
            referencia=documento_data.get('referencia', ''),
            data=documento_data.get('data', '')
        )
        fonograma.documentos_list.append(documento)
    
    return fonograma


def salvar_fonogramas_do_dataframe(df, app_context, salvar_apenas_validos=True, user_id=None):
    """Salva fonogramas do DataFrame no banco de dados"""
    salvos = 0
    atualizados = 0
    erros = []
    
    with app_context:
        for idx, (_, row) in enumerate(df.iterrows()):
            try:
                # Converter Series para dict e tratar valores NaN
                row_dict = row.to_dict()
                # Converter NaN para string vazia
                for key, val in row_dict.items():
                    if pd.isna(val):
                        row_dict[key] = ''
                    else:
                        row_dict[key] = str(val).strip() if not isinstance(val, (int, float)) else val
                
                isrc = str(row_dict.get('isrc', '')).strip()
                if not isrc:
                    continue
                
                # Verifica se já existe
                fonograma_existente = Fonograma.query.filter_by(isrc=isrc).first()
                
                if fonograma_existente:
                    # Atualiza existente
                    fonograma = atualizar_fonograma_do_dataframe(fonograma_existente, row_dict)
                    atualizados += 1
                else:
                    # Cria novo
                    fonograma = criar_fonograma_do_dataframe(row_dict)
                    # IMPORTANTE: Atribuir user_id para ownership
                    if user_id:
                        fonograma.user_id = user_id
                    db.session.add(fonograma)
                    salvos += 1
                
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                erros.append({
                    'linha': idx + 2,
                    'isrc': str(row_dict.get('isrc', '')),
                    'erro': str(e)
                })
    
    return {
        'salvos': salvos,
        'atualizados': atualizados,
        'erros': erros
    }


def atualizar_fonograma_do_dataframe(fonograma: Fonograma, row: Dict) -> Fonograma:
    """Atualiza um fonograma existente com dados do DataFrame"""
    fonograma.titulo = row.get('titulo', '').strip()
    fonograma.versao = row.get('versao', '').strip() or None
    fonograma.duracao = row.get('duracao', '').strip()
    fonograma.ano_grav = int(row.get('ano_grav', '')) if row.get('ano_grav', '').strip() else None
    fonograma.ano_lanc = int(row.get('ano_lanc', '')) if row.get('ano_lanc', '').strip() else None
    fonograma.idioma = row.get('idioma', '').strip() or None
    fonograma.genero = row.get('genero', '').strip()
    fonograma.cod_interno = row.get('cod_interno', '').strip() or None
    fonograma.titulo_obra = row.get('titulo_obra', '').strip()
    fonograma.cod_obra = row.get('cod_obra', '').strip() or None
    fonograma.cod_obra = row.get('cod_obra', '').strip() or None
    
    # Novos campos
    fonograma.pais_origem = row.get('pais_origem', '').strip() or None
    fonograma.paises_adicionais = row.get('paises_adicionais', '').strip() or None
    fonograma.flag_nacional = row.get('flag_nacional', '').strip() or None
    fonograma.classificacao_trilha = row.get('classificacao_trilha', '').strip() or None
    fonograma.tipo_arranjo = row.get('tipo_arranjo', '').strip() or None
    fonograma.subdivisao_estrangeiro = row.get('subdivisao_estrangeiro', '').strip() or None
    fonograma.publicacao_simultanea = bool(row.get('publicacao_simultanea')) if row.get('publicacao_simultanea') else False
    
    fonograma.prod_nome = row.get('prod_nome', '').strip()
    fonograma.prod_doc = limpar_documento(row.get('prod_doc', ''))
    fonograma.prod_fantasia = row.get('prod_fantasia', '').strip() or None
    fonograma.prod_endereco = row.get('prod_endereco', '').strip() or None
    fonograma.prod_perc = float(str(row.get('prod_perc', '0')).replace('%', '').replace(',', '.')) if row.get('prod_perc', '').strip() else 0.0
    fonograma.prod_assoc = row.get('prod_assoc', '').strip() or None
    fonograma.prod_data_ini = row.get('prod_data_ini', '').strip() or None
    fonograma.tipo_lanc = row.get('tipo_lanc', '').strip() or None
    fonograma.album = row.get('album', '').strip() or None
    fonograma.faixa = int(row.get('faixa', '')) if row.get('faixa', '').strip() else None
    fonograma.selo = row.get('selo', '').strip() or None
    fonograma.formato = row.get('formato', '').strip() or None
    fonograma.pais = row.get('pais', '').strip() or None
    fonograma.data_lanc = row.get('data_lanc', '').strip() or None
    fonograma.assoc_gestao = row.get('assoc_gestao', '').strip() or None
    fonograma.data_cad = row.get('data_cad', '').strip() or None
    fonograma.situacao = row.get('situacao', '').strip() or 'ATIVO'
    fonograma.obs_juridicas = row.get('obs_juridicas', '').strip() or None
    fonograma.historico = row.get('historico', '').strip() or None
    fonograma.territorio = row.get('territorio', '').strip() or None
    fonograma.tipos_exec = row.get('tipos_exec', '').strip() or None
    fonograma.prioridade = row.get('prioridade', '').strip() or None
    fonograma.cod_ecad = row.get('cod_ecad', '').strip() or None
    
    # Remove relacionamentos antigos
    Autor.query.filter_by(fonograma_id=fonograma.id).delete()
    Editora.query.filter_by(fonograma_id=fonograma.id).delete()
    Interprete.query.filter_by(fonograma_id=fonograma.id).delete()
    Musico.query.filter_by(fonograma_id=fonograma.id).delete()
    Documento.query.filter_by(fonograma_id=fonograma.id).delete()
    
    # Adiciona novos relacionamentos
    autores_input = row.get('autores')
    if isinstance(autores_input, list):
        autores_data = autores_input
    else:
        autores_data = parse_autores(autores_input or '')
    for autor_data in autores_data:
        autor = Autor(
            nome=autor_data['nome'],
            cpf=autor_data['cpf'],
            funcao=autor_data['funcao'],
            percentual=autor_data['percentual'],
            cae_ipi=autor_data.get('cae_ipi') or None,
            data_nascimento=autor_data.get('data_nascimento') or None,
            nacionalidade=autor_data.get('nacionalidade') or None
        )
        fonograma.autores_list.append(autor)
    
    editoras_input = row.get('editoras')
    if isinstance(editoras_input, list):
        editoras_data = editoras_input
    else:
        editoras_data = parse_editoras(editoras_input or '')
    for editora_data in editoras_data:
        editora = Editora(
            nome=editora_data['nome'],
            cnpj=editora_data['cnpj'],
            percentual=editora_data['percentual'],
            nacionalidade=editora_data.get('nacionalidade') or None
        )
        fonograma.editoras_list.append(editora)
    
    interpretes_input = row.get('interpretes')
    if isinstance(interpretes_input, list):
        interpretes_data = interpretes_input
    else:
        interpretes_data = parse_interpretes(interpretes_input or '')
    for interprete_data in interpretes_data:
        interprete = Interprete(
            nome=interprete_data['nome'],
            doc=interprete_data['doc'],
            categoria=interprete_data['categoria'],
            percentual=interprete_data['percentual'],
            associacao=interprete_data.get('associacao', '') or None,
            cae_ipi=interprete_data.get('cae_ipi') or None,
            data_nascimento=interprete_data.get('data_nascimento') or None,
            nacionalidade=interprete_data.get('nacionalidade') or None
        )
        fonograma.interpretes_list.append(interprete)
    
    musicos_input = row.get('musicos')
    if isinstance(musicos_input, list):
        musicos_data = musicos_input
    else:
        musicos_data = parse_musicos(musicos_input or '')
    for musico_data in musicos_data:
        musico = Musico(
            nome=musico_data['nome'],
            cpf=musico_data['cpf'],
            instrumento=musico_data['instrumento'],
            tipo=musico_data['tipo'],
            percentual=musico_data['percentual']
        )
        fonograma.musicos_list.append(musico)
    
    documentos_input = row.get('documentos')
    if isinstance(documentos_input, list):
        documentos_data = documentos_input
    else:
        documentos_data = parse_documentos(documentos_input or '')
    for documento_data in documentos_data:
        documento = Documento(
            tipo=documento_data['tipo'],
            referencia=documento_data.get('referencia', ''),
            data=documento_data.get('data', '')
        )
        fonograma.documentos_list.append(documento)
    
    return fonograma

