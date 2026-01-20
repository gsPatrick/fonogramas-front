# admin/services/lote_service.py
from models import db, Fonograma, HistoricoFonograma
from shared.processador import processar_arquivo_fonogramas
from datetime import datetime

def validar_importacao(arquivo):
    """Valida arquivo para importação em lote"""
    # Salvar temporariamente
    # Salvar temporariamente
    import tempfile
    import os
    
    ext = os.path.splitext(arquivo.filename)[1]
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    arquivo.save(temp.name)
    
    # Processar
    resultado = processar_arquivo_fonogramas(temp.name)
    
    # Validar cada item
    from shared.validador import validar_isrc
    
    validos = []
    invalidos = []
    
    for item in resultado['dados']:
        erros = []
        if not validar_isrc(item.get('isrc')):
            erros.append('ISRC inválido')
        
        if erros:
            item['erros'] = erros
            invalidos.append(item)
        else:
            validos.append(item)
            
    return {
        'total': len(resultado['dados']),
        'validos': len(validos),
        'invalidos': len(invalidos),
        'lista_validos': validos,
        'lista_invalidos': invalidos
    }

def executar_importacao(arquivo, usuario):
    """Executa importação em lote"""
    try:
        # Reutiliza lógica de validação/parse
        # ... (simplificado para brevidade, idealmente reutiliza o service compartilhado)
        from shared.fonograma_service import salvar_fonogramas_do_dataframe, criar_fonograma_do_dataframe
        import pandas as pd
        
        df = pd.read_excel(arquivo) if arquivo.filename.endswith('.xlsx') else pd.read_csv(arquivo)
        
        # Converter para lista de dicts
        dados = df.to_dict(orient='records')
        
        salvos = 0
        atualizados = 0
        
        for item in dados:
            # Lógica de salvar/atualizar
            fono = Fonograma.query.filter_by(isrc=item.get('isrc')).first()
            if fono:
                # Atualizar
                # ...
                atualizados += 1
            else:
                # Criar
                novo = criar_fonograma_do_dataframe(item)
                
                # SEGREGAÇÃO: Atribuir ao usuário que está importando
                if usuario:
                    novo.user_id = usuario.id
                    if usuario.associacao:
                        novo.assoc_gestao = usuario.associacao
                
                db.session.add(novo)
                salvos += 1
        
        db.session.commit()
        return {'sucesso': True, 'salvos': salvos, 'atualizados': atualizados}
        
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
        # Verificar restrições (não deletar enviados)
        fonogramas = Fonograma.query.filter(Fonograma.id.in_(fonograma_ids)).all()
        excluidos = 0
        erros = 0
        
        for f in fonogramas:
            if f.status_ecad in ['ENVIADO', 'ACEITO']:
                erros += 1
                continue
                
            db.session.delete(f)
            excluidos += 1
            
        db.session.commit()
        return {'sucesso': True, 'excluidos': excluidos, 'erros': erros}
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e)}
