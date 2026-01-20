# usuario/services/fonograma_service.py
from models import db, Fonograma, HistoricoFonograma
from datetime import datetime
from sqlalchemy import or_

def obter_estatisticas_usuario(usuario):
    """Estatísticas dos fonogramas do usuário (Filtro por ID)"""
    query = Fonograma.query.filter_by(user_id=usuario.id)
    
    total = query.count()
    pendentes = query.filter(Fonograma.status_ecad.in_([None, 'PENDENTE'])).count()
    enviados = Fonograma.query.filter_by(status_ecad='ENVIADO', user_id=usuario.id).count()
    aceitos = Fonograma.query.filter_by(status_ecad='ACEITO', user_id=usuario.id).count()
    
    return {
        'total': total,
        'pendentes': pendentes,
        'enviados': enviados,
        'aceitos': aceitos
    }

def obter_fonogramas_recentes(usuario, limit=10):
    """Últimos fonogramas cadastrados pelo usuário"""
    return Fonograma.query.filter_by(user_id=usuario.id)\
        .order_by(Fonograma.created_at.desc())\
        .limit(limit).all()

def listar_fonogramas(usuario, page=1, per_page=20, busca='', genero=None):
    """Lista fonogramas com filtros e paginação (Ownership enforce)"""
    query = Fonograma.query.filter_by(user_id=usuario.id)
    
    if busca:
        query = query.filter(
            or_(
                Fonograma.isrc.ilike(f'%{busca}%'),
                Fonograma.titulo.ilike(f'%{busca}%'),
                Fonograma.titulo_obra.ilike(f'%{busca}%')
            )
        )
    
    if genero:
        query = query.filter_by(genero=genero)
    
    return query.order_by(Fonograma.created_at.desc()).paginate(page=page, per_page=per_page)

def listar_todos_fonogramas(usuario):
    """Lista todos os fonogramas do usuário"""
    return Fonograma.query.filter_by(user_id=usuario.id)\
        .order_by(Fonograma.created_at.desc()).all()

def obter_fonograma(fonograma_id, usuario):
    """Obtém fonograma verificando propriedade"""
    fonograma = Fonograma.query.get(fonograma_id)
    
    if not fonograma:
        return None
    
    # Verificação de segurança: O usuário é dono?
    if fonograma.user_id != usuario.id:
        return None
    
    return fonograma

def obter_status_simplificado(fonograma):
    """Retorna status em linguagem amigável"""
    mapa_status = {
        None: {'texto': 'Pendente', 'cor': 'secondary', 'icone': 'clock'},
        'PENDENTE': {'texto': 'Pendente', 'cor': 'secondary', 'icone': 'clock'},
        'ENVIADO': {'texto': 'Enviado ao ECAD', 'cor': 'info', 'icone': 'send'},
        'ACEITO': {'texto': 'Aceito pelo ECAD', 'cor': 'success', 'icone': 'check-circle'},
        'RECUSADO': {'texto': 'Requer correção', 'cor': 'danger', 'icone': 'alert-circle'},
    }
    
    return mapa_status.get(fonograma.status_ecad, mapa_status[None])

def criar_fonograma(dados, usuario):
    """Cria novo fonograma vinculado ao usuário"""
    from shared.fonograma_service import criar_fonograma_do_dataframe
    from shared.validador import validar_isrc
    
    erros = []
    
    # Validações básicas
    if not dados.get('isrc'):
        erros.append({'campo': 'isrc', 'erro': 'ISRC é obrigatório'})
    elif not validar_isrc(dados.get('isrc')):
        erros.append({'campo': 'isrc', 'erro': 'ISRC inválido'})
    
    # Verificar se ISRC já existe
    if Fonograma.query.filter_by(isrc=dados.get('isrc')).first():
        erros.append({'campo': 'isrc', 'erro': 'ISRC já cadastrado'})
    
    if erros:
        return {'sucesso': False, 'erros': erros}
    
    try:
        fonograma = criar_fonograma_do_dataframe(dados)
        
        # VINCULO DE PROPRIEDADE (Ownership)
        fonograma.user_id = usuario.id
        
        # Preencher associação automaticamente do perfil do usuário
        if usuario.associacao:
            fonograma.assoc_gestao = usuario.associacao
        
        db.session.add(fonograma)
        
        # Registrar no histórico
        historico = HistoricoFonograma(
            fonograma_id=fonograma.id,
            data_alteracao=datetime.utcnow(),
            tipo_alteracao='CRIACAO',
            usuario=usuario.email,
            motivo='Criação manual via interface'
        )
        db.session.add(historico)
        
        db.session.commit()
        
        return {'sucesso': True, 'fonograma_id': fonograma.id}
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e)}

def atualizar_fonograma(fonograma, dados, usuario):
    """Atualiza fonograma existente (com verificação de dono)"""
    from shared.fonograma_service import atualizar_fonograma_do_dataframe
    
    # Segurança extra: garantir que está editando o próprio registro
    if fonograma.user_id != usuario.id:
        return {'sucesso': False, 'erro': 'Acesso negado: Você não é o titular deste fonograma.'}
    
    try:
        # Guardar valores anteriores para histórico
        valor_anterior = fonograma.to_dict(include_relations=False)
        
        fonograma = atualizar_fonograma_do_dataframe(fonograma, dados)
        
        # Registrar no histórico
        historico = HistoricoFonograma(
            fonograma_id=fonograma.id,
            data_alteracao=datetime.utcnow(),
            tipo_alteracao='EDICAO',
            usuario=usuario.email,
            motivo='Edição via interface',
            valor_anterior=str(valor_anterior),
            valor_novo=str(fonograma.to_dict(include_relations=False))
        )
        db.session.add(historico)
        
        db.session.commit()
        
        return {'sucesso': True}
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e)}

def excluir_fonograma(fonograma, usuario):
    """Exclui fonograma (com verificação de dono)"""
    
    if fonograma.user_id != usuario.id:
        return {'sucesso': False, 'erro': 'Acesso negado.'}

    try:
        db.session.delete(fonograma)
        db.session.commit()
        return {'sucesso': True}
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e)}

def obter_historico_usuario(usuario, page=1, per_page=20):
    """Obtém histórico de alterações feitas pelo usuário"""
    return HistoricoFonograma.query.filter_by(usuario=usuario.email)\
        .order_by(HistoricoFonograma.data_alteracao.desc())\
        .paginate(page=page, per_page=per_page)
