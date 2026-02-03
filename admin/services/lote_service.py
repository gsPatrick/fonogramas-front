# admin/services/lote_service.py
from models import db, Fonograma, HistoricoFonograma
from shared.processador import processar_arquivo_fonogramas
from datetime import datetime

def validar_importacao(arquivo):
    """Valida arquivo para importação em lote"""
    import tempfile
    import os
    
    ext = os.path.splitext(arquivo.filename)[1]
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    arquivo.save(temp.name)
    
    # Processar
    resultado = processar_arquivo_fonogramas(temp.name)
    
    # Validar cada item
    from shared.validador import (
        validar_isrc, validar_duracao, validar_ano, 
        validar_genero, validar_cpf, validar_cnpj, limpar_documento,
        GENEROS
    )
    
    validos = []
    invalidos = []
    erros_agrupados = {}  # Agrupar erros por tipo
    avisos_agrupados = {}  # Agrupar avisos por tipo (campos opcionais com valor inválido)
    
    for idx, item in enumerate(resultado['dados'], start=2):  # Linha 2 em diante (1 é header)
        erros = []
        avisos = []
        isrc = str(item.get('isrc', '')).strip()
        titulo = str(item.get('titulo', '')).strip()[:30]  # Primeiros 30 chars
        
        # === VALIDAÇÕES OBRIGATÓRIAS (bloqueiam importação) ===
        if not isrc:
            erros.append('ISRC vazio')
        elif not validar_isrc(isrc):
            erros.append('ISRC inválido')
        
        if not titulo:
            erros.append('Título vazio')
        
        # === VALIDAÇÕES OPCIONAIS (avisos, não bloqueiam) ===
        
        # Duração (formato MM:SS)
        duracao = str(item.get('duracao', '')).strip()
        if duracao and not validar_duracao(duracao):
            avisos.append(f'Duração inválida ({duracao}) - formato esperado: MM:SS')
        
        # Ano de gravação (1900-2100)
        ano_grav = str(item.get('ano_grav', '')).strip()
        if ano_grav and not validar_ano(ano_grav):
            avisos.append(f'Ano de gravação inválido ({ano_grav})')
        
        # Ano de lançamento (1900-2100)
        ano_lanc = str(item.get('ano_lanc', '')).strip()
        if ano_lanc and not validar_ano(ano_lanc):
            avisos.append(f'Ano de lançamento inválido ({ano_lanc})')
        
        # Gênero (lista permitida)
        genero = str(item.get('genero', '')).strip()
        if genero and not validar_genero(genero):
            avisos.append(f'Gênero não reconhecido ({genero}) - permitidos: {", ".join(GENEROS[:5])}...')
        
        # CPF/CNPJ do produtor
        prod_doc = str(item.get('prod_doc', '')).strip()
        if prod_doc:
            doc_limpo = limpar_documento(prod_doc)
            if len(doc_limpo) == 11:
                if not validar_cpf(prod_doc):
                    avisos.append(f'CPF do produtor inválido ({prod_doc})')
            elif len(doc_limpo) == 14:
                if not validar_cnpj(prod_doc):
                    avisos.append(f'CNPJ do produtor inválido ({prod_doc})')
            elif doc_limpo:
                avisos.append(f'Documento do produtor inválido ({prod_doc}) - esperado CPF ou CNPJ')
        
        # Processar erros e avisos
        if erros:
            item['linha'] = idx
            item['erros'] = erros
            item['avisos'] = avisos
            invalidos.append(item)
            
            # Agrupar por tipo de erro
            for erro in erros:
                if erro not in erros_agrupados:
                    erros_agrupados[erro] = []
                erros_agrupados[erro].append({
                    'linha': idx,
                    'isrc': isrc or '(vazio)',
                    'titulo': titulo or '(sem título)'
                })
        else:
            item['avisos'] = avisos
            validos.append(item)
        
        # Agrupar avisos (para relatório)
        for aviso in avisos:
            # Simplificar chave do aviso (remover valores específicos)
            chave_aviso = aviso.split('(')[0].strip()
            if chave_aviso not in avisos_agrupados:
                avisos_agrupados[chave_aviso] = []
            avisos_agrupados[chave_aviso].append({
                'linha': idx,
                'isrc': isrc or '(vazio)',
                'detalhe': aviso
            })
            
    return {
        'total': len(resultado['dados']),
        'validos': len(validos),
        'invalidos': len(invalidos),
        'com_avisos': len([v for v in validos if v.get('avisos')]),
        'lista_validos': validos,
        'lista_invalidos': invalidos,
        'erros_agrupados': erros_agrupados,
        'avisos_agrupados': avisos_agrupados
    }

def executar_importacao(arquivo, usuario):
    """Executa importação em lote"""
    try:
        from shared.fonograma_service import criar_fonograma_do_dataframe
        import pandas as pd
        
        # Ler arquivo
        if arquivo.filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(arquivo)
        else:
            df = pd.read_csv(arquivo, encoding='utf-8', on_bad_lines='skip')
        
        # Converter para lista de dicts
        dados = df.to_dict(orient='records')
        
        salvos = 0
        atualizados = 0
        erros = 0
        
        for item in dados:
            try:
                isrc = str(item.get('isrc', '')).strip()
                if not isrc:
                    erros += 1
                    continue
                
                # Verificar se já existe
                fono = Fonograma.query.filter_by(isrc=isrc).first()
                
                if fono:
                    # Atualizar campos existentes
                    fono.titulo = str(item.get('titulo', fono.titulo)).strip() if item.get('titulo') else fono.titulo
                    fono.versao = str(item.get('versao', '')).strip() or fono.versao
                    fono.duracao = str(item.get('duracao', fono.duracao)).strip() if item.get('duracao') else fono.duracao
                    fono.ano_grav = int(item.get('ano_grav')) if item.get('ano_grav') else fono.ano_grav
                    fono.ano_lanc = int(item.get('ano_lanc')) if item.get('ano_lanc') else fono.ano_lanc
                    fono.idioma = str(item.get('idioma', '')).strip() or fono.idioma
                    fono.genero = str(item.get('genero', fono.genero)).strip() if item.get('genero') else fono.genero
                    fono.titulo_obra = str(item.get('titulo_obra', '')).strip() or fono.titulo_obra
                    fono.prod_nome = str(item.get('prod_nome', '')).strip() or fono.prod_nome
                    fono.prod_doc = str(item.get('prod_doc', '')).strip() or fono.prod_doc
                    fono.updated_at = datetime.utcnow()
                    atualizados += 1
                else:
                    # Criar novo fonograma
                    novo = criar_fonograma_do_dataframe(item)
                    
                    # Atribuir ao usuário que está importando
                    if usuario:
                        novo.user_id = usuario.id
                        if hasattr(usuario, 'associacao') and usuario.associacao:
                            novo.assoc_gestao = usuario.associacao
                    
                    db.session.add(novo)
                    salvos += 1
                    
            except Exception as item_error:
                erros += 1
                continue
        
        db.session.commit()
        return {'sucesso': True, 'salvos': salvos, 'atualizados': atualizados, 'erros': erros}
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e)}

def atualizar_status_em_lote(fonograma_ids, novo_status, motivo, usuario):
    """Atualiza status de múltiplos fonogramas"""
    try:
        fonogramas = Fonograma.query.filter(Fonograma.id.in_(fonograma_ids)).all()
        atualizados = 0
        
        for f in fonogramas:
            valor_anterior = f.status_ecad
            f.status_ecad = novo_status
            
            # Histórico
            hist = HistoricoFonograma(
                fonograma_id=f.id,
                data_alteracao=datetime.utcnow(),
                tipo_alteracao='EDICAO_LOTE',
                campo_alterado='status_ecad',
                valor_anterior=valor_anterior,
                valor_novo=novo_status,
                usuario=usuario.email,
                motivo=motivo
            )
            db.session.add(hist)
            atualizados += 1
            
        db.session.commit()
        return {'sucesso': True, 'atualizados': atualizados}
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e)}

def excluir_em_lote(fonograma_ids, usuario):
    """Exclui múltiplos fonogramas"""
    try:
        # Converter IDs para inteiros
        ids_int = []
        for id_str in fonograma_ids:
            try:
                ids_int.append(int(id_str))
            except (ValueError, TypeError):
                continue
        
        if not ids_int:
            return {'sucesso': False, 'erro': 'Nenhum ID válido fornecido', 'excluidos': 0}
        
        # Buscar fonogramas
        fonogramas = Fonograma.query.filter(Fonograma.id.in_(ids_int)).all()
        
        if not fonogramas:
            return {'sucesso': False, 'erro': f'Nenhum fonograma encontrado com os IDs: {ids_int}', 'excluidos': 0}
        
        excluidos = 0
        
        for f in fonogramas:
            db.session.delete(f)
            excluidos += 1
            
        db.session.commit()
        return {'sucesso': True, 'excluidos': excluidos}
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e), 'excluidos': 0}
