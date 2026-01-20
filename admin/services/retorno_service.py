# admin/services/retorno_service.py
from shared.processador_retorno_ecad import processar_retorno, importar_retorno_ecad
from models import db, EnvioECAD

def processar_upload_retorno(arquivo, envio_id):
    """Processa arquivo de retorno do ECAD"""
    try:
        envio = EnvioECAD.query.get(envio_id)
        if not envio:
            return {'sucesso': False, 'erro': 'Envio não encontrado'}
            
        # Salvar arquivo
        import os
        import uuid
        ext = os.path.splitext(arquivo.filename)[1]
        filename = f"RET-{uuid.uuid4().hex[:8]}{ext}"
        path = os.path.join('uploads/retornos', filename)
        os.makedirs('uploads/retornos', exist_ok=True)
        arquivo.save(path)
        
        # Importar
        dados_retorno = importar_retorno_ecad(path, envio_id)
        
        # Processar
        resultado = processar_retorno(dados_retorno, envio_id)
        
        # Atualizar status do envio se todos processados
        envio.status = 'PROCESSADO'
        db.session.commit()
        
        return {
            'sucesso': True,
            'aceitos': resultado.get('aceitos', 0),
            'recusados': resultado.get('recusados', 0),
            'total': resultado.get('total_processados', 0)
        }
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e)}
