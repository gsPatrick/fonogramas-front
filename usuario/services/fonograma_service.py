# usuario/services/fonograma_service.py
from models import db, Fonograma, HistoricoFonograma
from datetime import datetime
from sqlalchemy import or_

def obter_estatisticas_usuario(usuario):
    """Estatísticas dos fonogramas do usuário (Filtro por ID)"""
    query = Fonograma.query.filter_by(user_id=usuario.id)
    
    total = query.count()
    nao_enviados = query.filter(or_(Fonograma.status_ecad.is_(None), Fonograma.status_ecad == 'NAO_ENVIADO')).count()
    enviados = Fonograma.query.filter_by(status_ecad='ENVIADO', user_id=usuario.id).count()
    aceitos = Fonograma.query.filter_by(status_ecad='ACEITO', user_id=usuario.id).count()
    recusados = Fonograma.query.filter_by(status_ecad='RECUSADO', user_id=usuario.id).count()
    pendentes = query.filter(Fonograma.status_ecad.in_([None, 'PENDENTE', 'NAO_ENVIADO'])).count()
    
    return {
        'total': total,
        'nao_enviados': nao_enviados,
        'pendentes': pendentes,
        'enviados': enviados,
        'aceitos': aceitos,
        'recusados': recusados
    }

def obter_fonogramas_recentes(usuario, limit=10):
    """Últimos fonogramas cadastrados pelo usuário"""
    return Fonograma.query.filter_by(user_id=usuario.id)\
        .order_by(Fonograma.created_at.desc())\
        .limit(limit).all()

def listar_fonogramas(usuario, page=1, per_page=20, busca='', genero=None, 
                      status=None, prod_assoc=None, data_inicio=None, data_fim=None):
    """Lista fonogramas com filtros e paginação (Admin vê todos, usuário só os seus)"""
    if usuario.is_admin:
        query = Fonograma.query
    else:
        query = Fonograma.query.filter_by(user_id=usuario.id)
    
    # Filtro de busca (ISRC, título, título da obra, nome do produtor)
    if busca:
        query = query.filter(
            or_(
                Fonograma.isrc.ilike(f'%{busca}%'),
                Fonograma.titulo.ilike(f'%{busca}%'),
                Fonograma.titulo_obra.ilike(f'%{busca}%'),
                Fonograma.prod_nome.ilike(f'%{busca}%')
            )
        )
    
    # Filtro por gênero
    if genero:
        query = query.filter_by(genero=genero)
    
    # Filtro por status ECAD
    if status:
        if status == 'NAO_ENVIADO':
            query = query.filter(or_(Fonograma.status_ecad.is_(None), Fonograma.status_ecad == 'NAO_ENVIADO'))
        else:
            query = query.filter_by(status_ecad=status)
    
    # Filtro por associação do produtor
    if prod_assoc:
        query = query.filter_by(prod_assoc=prod_assoc)
    
    # Filtro por período de criação
    if data_inicio:
        query = query.filter(Fonograma.created_at >= data_inicio)
    if data_fim:
        query = query.filter(Fonograma.created_at <= data_fim)
    
    return query.order_by(Fonograma.created_at.desc()).paginate(page=page, per_page=per_page)

def listar_todos_fonogramas(usuario):
    """Lista todos os fonogramas do usuário"""
    return Fonograma.query.filter_by(user_id=usuario.id)\
        .order_by(Fonograma.created_at.desc()).all()

def obter_fonograma(fonograma_id, usuario):
    """Obtém fonograma verificando propriedade (Admin pode ver todos)"""
    fonograma = Fonograma.query.get(fonograma_id)
    
    if not fonograma:
        return None
    
    # Admin pode acessar qualquer fonograma
    if usuario.is_admin:
        return fonograma
    
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
        db.session.flush()  # Garante que o ID seja gerado
        
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
    """Atualiza fonograma existente (com verificação de dono ou admin)"""
    from shared.fonograma_service import atualizar_fonograma_do_dataframe
    
    # Segurança: Admin pode editar qualquer fonograma, usuário só o seu
    if not usuario.is_admin and fonograma.user_id != usuario.id:
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
    """Exclui fonograma (admin pode excluir qualquer um, usuário só o seu)"""
    
    # Segurança: Admin pode excluir qualquer fonograma, usuário só o seu
    if not usuario.is_admin and fonograma.user_id != usuario.id:
        return {'sucesso': False, 'erro': 'Acesso negado: Você não é o titular deste fonograma.'}

    try:
        # Registrar no histórico antes de excluir
        historico = HistoricoFonograma(
            fonograma_id=fonograma.id,
            data_alteracao=datetime.utcnow(),
            tipo_alteracao='EXCLUSAO',
            usuario=usuario.email,
            motivo=f'Exclusão via interface (ISRC: {fonograma.isrc})'
        )
        db.session.add(historico)
        
        db.session.delete(fonograma)
        db.session.commit()
        return {'sucesso': True}
        
    except Exception as e:
        db.session.rollback()
        return {'sucesso': False, 'erro': str(e)}

def obter_historico_usuario(usuario, page=1, per_page=20):
    """Obtém histórico de alterações feitas pelo usuário"""

def processar_dados_formulario(form):
    """
    Processa o formulário (request.form) para extrair listas de participantes
    e retorna um dicionário compatível com criar_fonograma_do_dataframe (shared).
    """
    dados = form.to_dict(flat=True)
    
    # --- AUTORES ---
    autores = []
    nomes = form.getlist('autores_nome[]')
    cpfs = form.getlist('autores_cpf[]')
    funcoes = form.getlist('autores_funcao[]')
    percs = form.getlist('autores_percentual[]')
    caes = form.getlist('autores_cae[]')
    nacs = form.getlist('autores_nacionalidade[]')
    dtnascs = form.getlist('autores_dtnasc[]') # Data Nascimento
    
    for i in range(len(nomes)):
        if nomes[i] and nomes[i].strip():
            autores.append({
                'nome': nomes[i].strip(),
                'cpf': cpfs[i].strip() if i < len(cpfs) else '',
                'funcao': funcoes[i].strip() if i < len(funcoes) else 'AUTOR',
                'percentual': float(percs[i].replace(',', '.')) if i < len(percs) and percs[i] else 0.0,
                'cae_ipi': caes[i].strip() if i < len(caes) else None,
                'nacionalidade': nacs[i].strip() if i < len(nacs) else None,
                'data_nascimento': dtnascs[i].strip() if i < len(dtnascs) else None
            })
    if autores:
        dados['autores'] = autores

    # --- INTÉRPRETES ---
    interpretes = []
    nomes = form.getlist('interpretes_nome[]')
    docs = form.getlist('interpretes_doc[]')
    cats = form.getlist('interpretes_categoria[]')
    percs = form.getlist('interpretes_percentual[]')
    assocs = form.getlist('interpretes_assoc[]')
    caes = form.getlist('interpretes_cae[]')
    nacs = form.getlist('interpretes_nacionalidade[]')
    
    for i in range(len(nomes)):
        if nomes[i] and nomes[i].strip():
            interpretes.append({
                'nome': nomes[i].strip(),
                'doc': docs[i].strip() if i < len(docs) else '',
                'categoria': cats[i].strip() if i < len(cats) else 'INTERPRETE',
                'percentual': float(percs[i].replace(',', '.')) if i < len(percs) and percs[i] else 0.0,
                'associacao': assocs[i].strip() if i < len(assocs) else None,
                'cae_ipi': caes[i].strip() if i < len(caes) else None,
                'nacionalidade': nacs[i].strip() if i < len(nacs) else None
            })
    if interpretes:
        dados['interpretes'] = interpretes

    # --- MÚSICOS ---
    musicos = []
    nomes = form.getlist('musicos_nome[]')
    cpfs = form.getlist('musicos_cpf[]')
    insts = form.getlist('musicos_instrumento[]')
    tipos = form.getlist('musicos_tipo[]')
    percs = form.getlist('musicos_percentual[]')
    
    for i in range(len(nomes)):
        if nomes[i] and nomes[i].strip():
            musicos.append({
                'nome': nomes[i].strip(),
                'cpf': cpfs[i].strip() if i < len(cpfs) else '',
                'instrumento': insts[i].strip() if i < len(insts) else '',
                'tipo': tipos[i].strip() if i < len(tipos) else 'ACOMPANHANTE',
                'percentual': float(percs[i].replace(',', '.')) if i < len(percs) and percs[i] else 0.0
            })
    if musicos:
        dados['musicos'] = musicos
        
    return dados
