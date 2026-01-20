# admin/services/relatorio_service.py
from models import db, Fonograma, EnvioECAD, RetornoECAD
from sqlalchemy import func
from datetime import datetime, timedelta

def obter_metricas_gerais():
    """Retorna métricas gerais para o dashboard"""
    total_fonogramas = Fonograma.query.count()
    
    # Por status
    pendentes = Fonograma.query.filter(Fonograma.status_ecad.in_([None, 'PENDENTE'])).count()
    enviados = Fonograma.query.filter_by(status_ecad='ENVIADO').count()
    aceitos = Fonograma.query.filter_by(status_ecad='ACEITO').count()
    recusados = Fonograma.query.filter_by(status_ecad='RECUSADO').count()
    
    # Envios
    total_envios = EnvioECAD.query.count()
    envios_aguardando = EnvioECAD.query.filter_by(status='AGUARDANDO_RETORNO').count()
    
    # Taxa de aprovação
    total_retornos = RetornoECAD.query.count()
    retornos_aceitos = RetornoECAD.query.filter_by(status_ecad='ACEITO').count()
    taxa_aprovacao = (retornos_aceitos / total_retornos * 100) if total_retornos > 0 else 0
    
    # Últimos 30 dias
    data_30_dias = datetime.utcnow() - timedelta(days=30)
    novos_30_dias = Fonograma.query.filter(Fonograma.created_at >= data_30_dias).count()
    
    return {
        'total_fonogramas': total_fonogramas,
        'pendentes': pendentes,
        'enviados': enviados,
        'aceitos': aceitos,
        'recusados': recusados,
        'total_envios': total_envios,
        'envios_aguardando': envios_aguardando,
        'taxa_aprovacao': round(taxa_aprovacao, 1),
        'novos_30_dias': novos_30_dias,
    }

def obter_dados_dashboard():
    """Dados para gráficos do dashboard"""
    # Fonogramas por mês (últimos 12 meses)
    fonogramas_por_mes = db.session.query(
        func.strftime('%Y-%m', Fonograma.created_at).label('mes'),
        func.count(Fonograma.id).label('total')
    ).group_by('mes').order_by('mes').limit(12).all()
    
    # Por gênero
    por_genero = db.session.query(
        Fonograma.genero,
        func.count(Fonograma.id).label('total')
    ).group_by(Fonograma.genero).order_by(func.count(Fonograma.id).desc()).limit(10).all()
    
    # Por status
    por_status = db.session.query(
        Fonograma.status_ecad,
        func.count(Fonograma.id).label('total')
    ).group_by(Fonograma.status_ecad).all()
    
    return {
        'fonogramas_por_mes': [{'mes': m, 'total': t} for m, t in fonogramas_por_mes],
        'por_genero': [{'genero': g or 'N/A', 'total': t} for g, t in por_genero],
        'por_status': [{'status': s or 'PENDENTE', 'total': t} for s, t in por_status],
    }

def taxa_aprovacao():
    """Calcula taxa de aprovação detalhada"""
    # Por mês
    por_mes = db.session.query(
        func.strftime('%Y-%m', RetornoECAD.data_retorno).label('mes'),
        func.count(RetornoECAD.id).label('total'),
        func.sum(db.case((RetornoECAD.status_ecad == 'ACEITO', 1), else_=0)).label('aceitos')
    ).group_by('mes').order_by('mes').all()
    
    resultado = []
    for mes, total, aceitos in por_mes:
        taxa = (aceitos / total * 100) if total > 0 else 0
        resultado.append({
            'mes': mes,
            'total': total,
            'aceitos': aceitos,
            'recusados': total - aceitos,
            'taxa': round(taxa, 1)
        })
    
    return resultado

def fonogramas_pendentes():
    """Lista fonogramas pendentes ordenados por antiguidade"""
    return Fonograma.query.filter(
        Fonograma.status_ecad.in_([None, 'PENDENTE'])
    ).order_by(Fonograma.created_at.asc()).limit(100).all()

def distribuicao_por_genero():
    """Distribuição de fonogramas por gênero"""
    return db.session.query(
        Fonograma.genero,
        func.count(Fonograma.id).label('total')
    ).group_by(Fonograma.genero).order_by(func.count(Fonograma.id).desc()).all()

def fonogramas_por_produtor():
    """Fonogramas agrupados por produtor"""
    return db.session.query(
        Fonograma.prod_nome,
        func.count(Fonograma.id).label('total')
    ).group_by(Fonograma.prod_nome).order_by(func.count(Fonograma.id).desc()).limit(50).all()

def envios_por_periodo(data_inicio=None, data_fim=None):
    """Envios em um período específico"""
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
    
    query = EnvioECAD.query
    
    if data_inicio:
        query = query.filter(EnvioECAD.data_envio >= data_inicio)
    if data_fim:
        query = query.filter(EnvioECAD.data_envio <= data_fim)
    
    return query.order_by(EnvioECAD.data_envio.desc()).all()

def exportar_relatorio(tipo, data_inicio=None, data_fim=None):
    """Exporta relatório para Excel"""
    import pandas as pd
    from openpyxl import Workbook
    import tempfile
    
    # Obter dados baseado no tipo
    if tipo == 'aprovacao':
        dados = taxa_aprovacao()
        df = pd.DataFrame(dados)
    elif tipo == 'genero':
        dados = distribuicao_por_genero()
        df = pd.DataFrame(dados, columns=['Gênero', 'Total'])
    elif tipo == 'produtor':
        dados = fonogramas_por_produtor()
        df = pd.DataFrame(dados, columns=['Produtor', 'Total'])
    else:
        df = pd.DataFrame()
    
    # Salvar em arquivo temporário
    arquivo = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(arquivo.name, index=False)
    
    return arquivo.name
