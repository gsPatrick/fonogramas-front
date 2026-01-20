# admin/services/envio_service.py
from models import db, Fonograma, EnvioECAD, HistoricoFonograma
from shared.gerador_ecad import gerar_excel_ecad, gerar_exp_ecad, validar_antes_envio
from datetime import datetime
import uuid
import os

UPLOAD_FOLDER = 'uploads/envios'

def obter_fonogramas_para_envio():
    """Retorna fonogramas que podem ser enviados ao ECAD"""
    return Fonograma.query.filter(
        Fonograma.status_ecad.in_([None, 'PENDENTE', 'RECUSADO', 'NAO_ENVIADO'])
    ).order_by(Fonograma.created_at.desc()).all()

def validar_fonogramas_para_envio(fonograma_ids):
    """Valida fonogramas antes de criar envio"""
    fonogramas = Fonograma.query.filter(Fonograma.id.in_(fonograma_ids)).all()
    return validar_antes_envio(fonogramas)

def criar_envio(fonograma_ids, formato, usuario):
    """Cria um novo envio ao ECAD"""
    try:
        fonogramas = Fonograma.query.filter(Fonograma.id.in_(fonograma_ids)).all()
        
        if not fonogramas:
            return {'sucesso': False, 'erro': 'Nenhum fonograma selecionado'}
        
        # Validar antes
        validacao = validar_antes_envio(fonogramas)
        if validacao['com_erro'] > 0:
            return {
                'sucesso': False, 
                'erro': f'{validacao["com_erro"]} fonogramas com erro',
                'detalhes': validacao['erros']
            }
        
        # Gerar protocolo único
        protocolo = f"ECAD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Criar pasta se não existir
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Gerar arquivo
        if formato == 'EXCEL':
            arquivo_path = os.path.join(UPLOAD_FOLDER, f"{protocolo}.xlsx")
            resultado_arquivo = gerar_excel_ecad(fonogramas, arquivo_path)
        else:
            arquivo_path = os.path.join(UPLOAD_FOLDER, f"{protocolo}.exp")
            resultado_arquivo = gerar_exp_ecad(fonogramas, arquivo_path)
        
        # Criar registro de envio
        envio = EnvioECAD(
            protocolo=protocolo,
            data_envio=datetime.utcnow(),
            tipo_envio='PARCIAL' if len(fonogramas) < 100 else 'TOTAL',
            metodo='MANUAL',
            formato_arquivo=formato,
            arquivo_gerado=arquivo_path,
            total_fonogramas=len(fonogramas),
            status='AGUARDANDO_RETORNO',
            created_by=usuario.email if usuario else None
        )
        
        # Associar fonogramas
        for fono in fonogramas:
            envio.fonogramas.append(fono)
            
            # Guardar status ANTES de alterar
            status_anterior = fono.status_ecad
            
            # Atualizar status do fonograma
            fono.status_ecad = 'ENVIADO'
            fono.data_ultimo_envio = datetime.utcnow()
            fono.tentativas_envio = (fono.tentativas_envio or 0) + 1
            fono.ultimo_protocolo_ecad = protocolo
            
            # Registrar no histórico
            historico = HistoricoFonograma(
                fonograma_id=fono.id,
                data_alteracao=datetime.utcnow(),
                tipo_alteracao='ENVIO',
                campo_alterado='status_ecad',
                valor_anterior=status_anterior,
                valor_novo='ENVIADO',
                usuario=usuario.email if usuario else None,
                motivo=f'Envio ao ECAD - Protocolo: {protocolo}'
            )
            db.session.add(historico)
        
        db.session.add(envio)
        db.session.commit()
        
        return {
            'sucesso': True,
            'envio_id': envio.id,
            'protocolo': protocolo,
            'arquivo': arquivo_path,
            'total': len(fonogramas)
        }
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e)}

def reenviar_recusados(envio_id, usuario):
    """Cria novo envio com fonogramas recusados"""
    from shared.processador_retorno_ecad import obter_fonogramas_para_reenvio
    
    fonograma_ids = obter_fonogramas_para_reenvio(envio_id)
    
    if not fonograma_ids:
        return {'sucesso': False, 'erro': 'Nenhum fonograma recusado para reenvio'}
    
    return criar_envio(fonograma_ids, 'EXCEL', usuario)
