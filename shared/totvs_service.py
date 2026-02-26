import requests
import os
import json
from datetime import datetime
from models import db, EcadLog

class TOTVSService:
    def __init__(self):
        self.base_url = os.environ.get('TOTVS_URL', 'http://localhost:8080/rest')
        self.auth = (os.environ.get('TOTVS_USER', 'admin'), os.environ.get('TOTVS_PASS', 'admin'))

    def enviar_fonograma(self, fono):
        """
        Mapeia e envia dados do fonograma para o Protheus (Tabela A1_NOME, A1_CGC etc para Titulares)
        Para Fonogramas, adaptamos para o modelo de Produto/Serviço ou Ativo conforme Protheus.
        """
        payload = {
            "isrc": fono.isrc,
            "titulo": fono.titulo,
            "projeto": fono.cod_interno,
            "produtor": {
                "nome": fono.prod_nome,
                "documento": fono.prod_doc, # A1_CGC
            },
            "data_gravacao": fono.ano_grav,
            "status": "ATIVO" if fono.status_ecad == 'ACEITO' else 'PENDENTE'
        }
        
        try:
            # Placeholder para a URL real do Protheus
            # response = requests.post(f"{self.base_url}/fonogramas", json=payload, auth=self.auth, timeout=10)
            # response.raise_for_status()
            
            # Log local da integração
            log = EcadLog(
                fonograma_id=fono.id,
                tipo='TOTVS_SYNC',
                descricao=f"Sincronização enviada para TOTVS: {fono.isrc}",
                usuario_id=fono.user_id
            )
            db.session.add(log)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Erro ao sincronizar com TOTVS: {str(e)}")
            return False

def sync_totvs_worker(fono_ids):
    """Worker para processamento em background (adaptado do TotvsWorker)"""
    from app import app
    from models import Fonograma
    
    with app.app_context():
        service = TOTVSService()
        for fono_id in fono_ids:
            fono = Fonograma.query.get(fono_id)
            if fono:
                service.enviar_fonograma(fono)
