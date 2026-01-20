# admin/services/auditoria_service.py
from models import db, Fonograma, HistoricoFonograma
from datetime import datetime
import pandas as pd
import tempfile

def obter_historico(page=1, tipo=None, data_inicio=None, data_fim=None):
    """Obtém histórico filtrado"""
    query = HistoricoFonograma.query
    
    # Converter strings para datetime se necessário
    if data_inicio and isinstance(data_inicio, str):
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        except ValueError:
            data_inicio = None
            
    if data_fim and isinstance(data_fim, str):
        try:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        except ValueError:
            data_fim = None
    
    if tipo:
        query = query.filter_by(tipo_alteracao=tipo)
    if data_inicio:
        query = query.filter(HistoricoFonograma.data_alteracao >= data_inicio)
    if data_fim:
        query = query.filter(HistoricoFonograma.data_alteracao <= data_fim)
        
    return query.order_by(HistoricoFonograma.data_alteracao.desc()).paginate(page=page, per_page=20)

def exportar_historico(data_inicio=None, data_fim=None):
    """Exporta histórico para Excel"""
    query = HistoricoFonograma.query
    
    # Converter strings para datetime se necessário
    if data_inicio and isinstance(data_inicio, str):
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        except ValueError:
            data_inicio = None
            
    if data_fim and isinstance(data_fim, str):
        try:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        except ValueError:
            data_fim = None
    
    if data_inicio:
        query = query.filter(HistoricoFonograma.data_alteracao >= data_inicio)
    if data_fim:
        query = query.filter(HistoricoFonograma.data_alteracao <= data_fim)
    
    historico = query.order_by(HistoricoFonograma.data_alteracao.desc()).all()
    
    dados = []
    for h in historico:
        dados.append({
            'Data': h.data_alteracao,
            'Fonograma ID': h.fonograma_id,
            'Tipo': h.tipo_alteracao,
            'Campo': h.campo_alterado,
            'Valor Anterior': h.valor_anterior,
            'Valor Novo': h.valor_novo,
            'Usuário': h.usuario,
            'Motivo': h.motivo
        })
    
    df = pd.DataFrame(dados)
    arquivo = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(arquivo.name, index=False)
    
    return arquivo.name
