"""
Serviço para operações CRUD de fonogramas
"""

from models import db, Fonograma, Autor, Editora, Interprete, Musico, Documento
from processador import parse_autores, parse_interpretes, parse_musicos, parse_editoras, parse_documentos
from validador import limpar_documento
from typing import Dict


def criar_fonograma_do_dataframe(row: Dict) -> Fonograma:
    """Cria um fonograma a partir de uma linha do DataFrame"""
    fonograma = Fonograma(
        isrc=row.get('isrc', '').strip(),
        titulo=row.get('titulo', '').strip(),
        versao=row.get('versao', '').strip() or None,
        duracao=row.get('duracao', '').strip(),
        ano_grav=int(row.get('ano_grav', '')) if row.get('ano_grav', '').strip() else None,
        ano_lanc=int(row.get('ano_lanc', '')) if row.get('ano_lanc', '').strip() else None,
        idioma=row.get('idioma', '').strip() or None,
        genero=row.get('genero', '').strip(),
        cod_interno=row.get('cod_interno', '').strip() or None,
        titulo_obra=row.get('titulo_obra', '').strip(),
        cod_obra=row.get('cod_obra', '').strip() or None,
        prod_nome=row.get('prod_nome', '').strip(),
        prod_doc=limpar_documento(row.get('prod_doc', '')),
        prod_fantasia=row.get('prod_fantasia', '').strip() or None,
        prod_endereco=row.get('prod_endereco', '').strip() or None,
        prod_perc=float(str(row.get('prod_perc', '0')).replace('%', '').replace(',', '.')) if row.get('prod_perc', '').strip() else 0.0,
        prod_assoc=row.get('prod_assoc', '').strip() or None,
        prod_data_ini=row.get('prod_data_ini', '').strip() or None,
        tipo_lanc=row.get('tipo_lanc', '').strip() or None,
        album=row.get('album', '').strip() or None,
        faixa=int(row.get('faixa', '')) if row.get('faixa', '').strip() else None,
        selo=row.get('selo', '').strip() or None,
        formato=row.get('formato', '').strip() or None,
        pais=row.get('pais', '').strip() or None,
        data_lanc=row.get('data_lanc', '').strip() or None,
        assoc_gestao=row.get('assoc_gestao', '').strip() or None,
        data_cad=row.get('data_cad', '').strip() or None,
        situacao=row.get('situacao', '').strip() or 'ATIVO',
        obs_juridicas=row.get('obs_juridicas', '').strip() or None,
        historico=row.get('historico', '').strip() or None,
        territorio=row.get('territorio', '').strip() or None,
        tipos_exec=row.get('tipos_exec', '').strip() or None,
        prioridade=row.get('prioridade', '').strip() or None,
        cod_ecad=row.get('cod_ecad', '').strip() or None,
    )
    
    # Adiciona autores
    autores_data = parse_autores(row.get('autores', ''))
    for autor_data in autores_data:
        autor = Autor(
            nome=autor_data['nome'],
            cpf=autor_data['cpf'],
            funcao=autor_data['funcao'],
            percentual=autor_data['percentual']
        )
        fonograma.autores_list.append(autor)
    
    # Adiciona editoras
    editoras_data = parse_editoras(row.get('editoras', ''))
    for editora_data in editoras_data:
        editora = Editora(
            nome=editora_data['nome'],
            cnpj=editora_data['cnpj'],
            percentual=editora_data['percentual']
        )
        fonograma.editoras_list.append(editora)
    
    # Adiciona intérpretes
    interpretes_data = parse_interpretes(row.get('interpretes', ''))
    for interprete_data in interpretes_data:
        interprete = Interprete(
            nome=interprete_data['nome'],
            doc=interprete_data['doc'],
            categoria=interprete_data['categoria'],
            percentual=interprete_data['percentual'],
            associacao=interprete_data.get('associacao', '') or None
        )
        fonograma.interpretes_list.append(interprete)
    
    # Adiciona músicos
    musicos_data = parse_musicos(row.get('musicos', ''))
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
    documentos_data = parse_documentos(row.get('documentos', ''))
    for documento_data in documentos_data:
        documento = Documento(
            tipo=documento_data['tipo'],
            referencia=documento_data.get('referencia', ''),
            data=documento_data.get('data', '')
        )
        fonograma.documentos_list.append(documento)
    
    return fonograma


def salvar_fonogramas_do_dataframe(df, app_context, salvar_apenas_validos=True):
    """Salva fonogramas do DataFrame no banco de dados"""
    salvos = 0
    atualizados = 0
    erros = []
    
    with app_context:
        for idx, (_, row) in enumerate(df.iterrows()):
            try:
                isrc = row.get('isrc', '').strip()
                if not isrc:
                    continue
                
                # Verifica se já existe
                fonograma_existente = Fonograma.query.filter_by(isrc=isrc).first()
                
                if fonograma_existente:
                    # Atualiza existente
                    fonograma = atualizar_fonograma_do_dataframe(fonograma_existente, row)
                    atualizados += 1
                else:
                    # Cria novo
                    fonograma = criar_fonograma_do_dataframe(row)
                    db.session.add(fonograma)
                    salvos += 1
                
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                erros.append({
                    'linha': idx + 2,
                    'isrc': row.get('isrc', ''),
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
    autores_data = parse_autores(row.get('autores', ''))
    for autor_data in autores_data:
        autor = Autor(
            nome=autor_data['nome'],
            cpf=autor_data['cpf'],
            funcao=autor_data['funcao'],
            percentual=autor_data['percentual']
        )
        fonograma.autores_list.append(autor)
    
    editoras_data = parse_editoras(row.get('editoras', ''))
    for editora_data in editoras_data:
        editora = Editora(
            nome=editora_data['nome'],
            cnpj=editora_data['cnpj'],
            percentual=editora_data['percentual']
        )
        fonograma.editoras_list.append(editora)
    
    interpretes_data = parse_interpretes(row.get('interpretes', ''))
    for interprete_data in interpretes_data:
        interprete = Interprete(
            nome=interprete_data['nome'],
            doc=interprete_data['doc'],
            categoria=interprete_data['categoria'],
            percentual=interprete_data['percentual'],
            associacao=interprete_data.get('associacao', '') or None
        )
        fonograma.interpretes_list.append(interprete)
    
    musicos_data = parse_musicos(row.get('musicos', ''))
    for musico_data in musicos_data:
        musico = Musico(
            nome=musico_data['nome'],
            cpf=musico_data['cpf'],
            instrumento=musico_data['instrumento'],
            tipo=musico_data['tipo'],
            percentual=musico_data['percentual']
        )
        fonograma.musicos_list.append(musico)
    
    documentos_data = parse_documentos(row.get('documentos', ''))
    for documento_data in documentos_data:
        documento = Documento(
            tipo=documento_data['tipo'],
            referencia=documento_data.get('referencia', ''),
            data=documento_data.get('data', '')
        )
        fonograma.documentos_list.append(documento)
    
    return fonograma

