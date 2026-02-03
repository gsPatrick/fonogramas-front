# admin/routes.py
from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from shared.decorators import admin_required
from models import db, Fonograma, EnvioECAD, RetornoECAD, HistoricoFonograma, User
from admin.services import envio_service, retorno_service, auditoria_service, lote_service, relatorio_service
from datetime import datetime
import os
from flask_login import current_user
from . import admin_bp

# ==================== DASHBOARD ====================

@admin_bp.route('/')
@admin_required
def dashboard():
    """Dashboard administrativo com métricas gerais"""
    stats = relatorio_service.obter_metricas_gerais()
    return render_template('admin/dashboard.html', stats=stats)

# ==================== ENVIOS ECAD ====================

@admin_bp.route('/envios')
@admin_required
def listar_envios():
    """Lista todos os envios ao ECAD"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = EnvioECAD.query.order_by(EnvioECAD.data_envio.desc())
    
    if status:
        query = query.filter_by(status=status)
    
    envios = query.paginate(page=page, per_page=per_page)
    return render_template('admin/envios/lista.html', envios=envios)

@admin_bp.route('/envios/novo', methods=['GET', 'POST'])
@admin_required
def novo_envio():
    """Criar novo envio ao ECAD"""
    if request.method == 'POST':
        fonograma_ids = request.form.getlist('fonograma_ids')
        formato = request.form.get('formato', 'EXCEL')
        
        resultado = envio_service.criar_envio(
            fonograma_ids=fonograma_ids,
            formato=formato,
            usuario=current_user
        )
        
        if resultado['sucesso']:
            flash(f'Envio criado com sucesso! Protocolo: {resultado["protocolo"]}', 'success')
            return redirect(url_for('admin.detalhes_envio', envio_id=resultado['envio_id']))
        else:
            flash(f'Erro ao criar envio: {resultado["erro"]}', 'danger')
    
    # GET: listar fonogramas disponíveis para envio
    fonogramas = envio_service.obter_fonogramas_para_envio()
    return render_template('admin/envios/novo.html', fonogramas=fonogramas)

@admin_bp.route('/envios/<int:envio_id>')
@admin_required
def detalhes_envio(envio_id):
    """Detalhes de um envio específico"""
    envio = EnvioECAD.query.get_or_404(envio_id)
    retornos = RetornoECAD.query.filter_by(envio_id=envio_id).all()
    return render_template('admin/envios/detalhes.html', envio=envio, retornos=retornos)

@admin_bp.route('/envios/<int:envio_id>/download')
@admin_required
def download_arquivo_envio(envio_id):
    """Download do arquivo gerado para envio"""
    envio = EnvioECAD.query.get_or_404(envio_id)
    if envio.arquivo_gerado and os.path.exists(envio.arquivo_gerado):
        return send_file(envio.arquivo_gerado, as_attachment=True)
    flash('Arquivo não encontrado.', 'danger')
    return redirect(url_for('admin.detalhes_envio', envio_id=envio_id))

@admin_bp.route('/envios/<int:envio_id>/reenviar', methods=['POST'])
@admin_required
def reenviar_recusados(envio_id):
    """Reenviar fonogramas recusados de um envio"""
    resultado = envio_service.reenviar_recusados(envio_id, current_user)
    
    if resultado['sucesso']:
        flash(f'Reenvio criado! Novo protocolo: {resultado["protocolo"]}', 'success')
        return redirect(url_for('admin.detalhes_envio', envio_id=resultado['envio_id']))
    else:
        flash(f'Erro: {resultado["erro"]}', 'danger')
        return redirect(url_for('admin.detalhes_envio', envio_id=envio_id))

@admin_bp.route('/envios/validar-selecao', methods=['POST'])
@admin_required
def validar_selecao_envio():
    """API: Valida fonogramas selecionados antes de gerar envio"""
    fonograma_ids = request.json.get('fonograma_ids', [])
    resultado = envio_service.validar_fonogramas_para_envio(fonograma_ids)
    return jsonify(resultado)

# ==================== RETORNOS ECAD ====================

@admin_bp.route('/retornos')
@admin_required
def listar_retornos():
    """Lista todos os retornos processados"""
    page = request.args.get('page', 1, type=int)
    retornos = RetornoECAD.query.order_by(RetornoECAD.data_retorno.desc()).paginate(page=page, per_page=20)
    return render_template('admin/retornos/lista.html', retornos=retornos)

@admin_bp.route('/retornos/upload', methods=['GET', 'POST'])
@admin_required
def upload_retorno():
    """Upload de arquivo de retorno do ECAD"""
    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo enviado.', 'danger')
            return redirect(request.url)
        
        arquivo = request.files['arquivo']
        envio_id = request.form.get('envio_id', type=int)
        
        if not envio_id:
            flash('Selecione o envio relacionado.', 'danger')
            return redirect(request.url)
        
        resultado = retorno_service.processar_upload_retorno(arquivo, envio_id)
        
        if resultado['sucesso']:
            flash(f'Retorno processado! Aceitos: {resultado["aceitos"]}, Recusados: {resultado["recusados"]}', 'success')
            return redirect(url_for('admin.detalhes_envio', envio_id=envio_id))
        else:
            flash(f'Erro: {resultado["erro"]}', 'danger')
    
    # GET: listar envios aguardando retorno
    envios_pendentes = EnvioECAD.query.filter_by(status='AGUARDANDO_RETORNO').all()
    return render_template('admin/retornos/upload.html', envios=envios_pendentes)

@admin_bp.route('/retornos/<int:retorno_id>')
@admin_required
def detalhes_retorno(retorno_id):
    """Detalhes de um retorno específico"""
    retorno = RetornoECAD.query.get_or_404(retorno_id)
    return render_template('admin/retornos/detalhes.html', retorno=retorno)

# ==================== AUDITORIA ====================

@admin_bp.route('/auditoria')
@admin_required
def auditoria_geral():
    """Visualização do histórico completo de alterações"""
    page = request.args.get('page', 1, type=int)
    tipo = request.args.get('tipo')  # CRIACAO, EDICAO, ENVIO, RETORNO
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    historico = auditoria_service.obter_historico(
        page=page,
        tipo=tipo,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    return render_template('admin/auditoria/lista.html', historico=historico)

@admin_bp.route('/auditoria/fonograma/<int:fonograma_id>')
@admin_required
def auditoria_fonograma(fonograma_id):
    """Histórico completo de um fonograma específico"""
    fonograma = Fonograma.query.get_or_404(fonograma_id)
    historico = HistoricoFonograma.query.filter_by(fonograma_id=fonograma_id)\
        .order_by(HistoricoFonograma.data_alteracao.desc()).all()
    return render_template('admin/auditoria/fonograma.html', fonograma=fonograma, historico=historico)

@admin_bp.route('/auditoria/exportar')
@admin_required
def exportar_auditoria():
    """Exporta histórico de auditoria para Excel"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    arquivo = auditoria_service.exportar_historico(data_inicio, data_fim)
    return send_file(arquivo, as_attachment=True, download_name='auditoria.xlsx')

# ==================== OPERAÇÕES EM LOTE ====================

@admin_bp.route('/lote')
@admin_required
def operacoes_lote():
    """Menu de operações em lote"""
    return render_template('admin/lote/menu.html')

@admin_bp.route('/lote/importar', methods=['GET', 'POST'])
@admin_required
def importar_lote():
    """Importação massiva de fonogramas (suporta múltiplos arquivos)"""
    if request.method == 'POST':
        arquivos = request.files.getlist('arquivo')
        if not arquivos or not arquivos[0].filename:
            flash('Nenhum arquivo enviado.', 'danger')
            return redirect(request.url)
        
        modo = request.form.get('modo', 'validar')
        
        if modo == 'validar':
            resultado_final = {
                'total_linhas': 0, 
                'linhas_validas': 0, 
                'linhas_com_erro': 0, 
                'linhas_com_avisos': 0,
                'erros_agrupados': {},
                'avisos_agrupados': {},
                'arquivos': []
            }
            
            for arquivo in arquivos:
                if not arquivo.filename: continue
                res = lote_service.validar_importacao(arquivo)
                
                resultado_final['total_linhas'] += res['total']
                resultado_final['linhas_validas'] += res['validos']
                resultado_final['linhas_com_erro'] += res['invalidos']
                resultado_final['linhas_com_avisos'] += res.get('com_avisos', 0)
                resultado_final['arquivos'].append(arquivo.filename)
                
                # Mesclar erros agrupados
                for tipo_erro, lista in res.get('erros_agrupados', {}).items():
                    if tipo_erro not in resultado_final['erros_agrupados']:
                        resultado_final['erros_agrupados'][tipo_erro] = []
                    for item in lista:
                        item['arquivo'] = arquivo.filename
                        resultado_final['erros_agrupados'][tipo_erro].append(item)
                
                # Mesclar avisos agrupados
                for tipo_aviso, lista in res.get('avisos_agrupados', {}).items():
                    if tipo_aviso not in resultado_final['avisos_agrupados']:
                        resultado_final['avisos_agrupados'][tipo_aviso] = []
                    for item in lista:
                        item['arquivo'] = arquivo.filename
                        resultado_final['avisos_agrupados'][tipo_aviso].append(item)

            return render_template('admin/lote/resultado_validacao.html', resultado=resultado_final)
            
        else:
            total_salvos = 0
            total_atualizados = 0
            erros_gerais = []
            
            for arquivo in arquivos:
                if not arquivo.filename: continue
                resultado = lote_service.executar_importacao(arquivo, current_user)
                
                if resultado['sucesso']:
                    total_salvos += resultado['salvos']
                    total_atualizados += resultado['atualizados']
                else:
                    erros_gerais.append(f"{arquivo.filename}: {resultado['erro']}")
            
            if not erros_gerais:
                flash(f'Importação concluída! Novos: {total_salvos}, Atualizados: {total_atualizados}', 'success')
            else:
                flash(f'Importação parcial. Novos: {total_salvos}, Atualizados: {total_atualizados}. Erros: {"; ".join(erros_gerais)}', 'warning')
                
            return redirect(url_for('admin.importar_lote'))
            
    return render_template('admin/lote/importar.html')

@admin_bp.route('/lote/template')
@admin_required
def download_template_lote():
    """Download do template Excel para importação em lote"""
    from usuario.services.upload_service import gerar_template
    
    # Gerar template (reutilizando serviço do usuário ou criando específico)
    # Aqui vamos usar uma versão simplificada ou reutilizar o do usuário se adequado
    # Para admin, vamos usar o mesmo gerador para consistência
    arquivo = gerar_template()
    
    return send_file(
        arquivo, 
        as_attachment=True, 
        download_name='template_importacao.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@admin_bp.route('/lote/atualizar-status', methods=['GET', 'POST'])
@admin_required
def atualizar_status_lote():
    """Atualização de status em lote"""
    if request.method == 'POST':
        fonograma_ids = request.form.getlist('fonograma_ids')
        novo_status = request.form.get('novo_status')
        motivo = request.form.get('motivo')
        
        resultado = lote_service.atualizar_status_em_lote(
            fonograma_ids=fonograma_ids,
            novo_status=novo_status,
            motivo=motivo,
            usuario=current_user
        )
        
        if resultado['sucesso']:
            flash(f'{resultado["atualizados"]} fonogramas atualizados.', 'success')
        else:
            flash(f'Erro: {resultado["erro"]}', 'danger')
    
    fonogramas = Fonograma.query.order_by(Fonograma.created_at.desc()).limit(500).all()
    return render_template('admin/lote/atualizar_status.html', fonogramas=fonogramas)

@admin_bp.route('/lote/excluir', methods=['GET', 'POST'])
@admin_required
def excluir_lote():
    """Exclusão em massa de fonogramas"""
    if request.method == 'POST':
        # Pega os IDs do textarea (separados por vírgula) ou dos checkboxes
        ids_texto = request.form.get('fonograma_ids_texto', '').strip()
        ids_checkbox = request.form.getlist('fonograma_ids')
        
        # Debug removido
        
        # Combina ambas as fontes de IDs
        fonograma_ids = []
        if ids_texto:
            fonograma_ids = [id.strip() for id in ids_texto.split(',') if id.strip()]
        if ids_checkbox:
            fonograma_ids.extend(ids_checkbox)
        
        # Remove duplicatas
        fonograma_ids = list(set(fonograma_ids))
        

        
        confirmar = request.form.get('confirmar')
        
        if not fonograma_ids:
            flash('Selecione pelo menos um fonograma para excluir.', 'warning')
            return redirect(request.url)
        
        if confirmar != 'CONFIRMAR':
            flash('Digite CONFIRMAR para executar a exclusão.', 'warning')
            return redirect(request.url)
        
        resultado = lote_service.excluir_em_lote(fonograma_ids, current_user)
        

        
        if resultado['sucesso']:
            flash(f'{resultado["excluidos"]} fonograma(s) excluído(s) com sucesso!', 'success')
        else:
            flash(f'Erro: {resultado.get("erro", "Erro desconhecido")} (IDs recebidos: {fonograma_ids})', 'danger')
        
        return redirect(request.url)
    
    # Busca todos os fonogramas para exibir na tabela
    from models import Fonograma, User
    fonogramas = db.session.query(
        Fonograma.id,
        Fonograma.titulo,
        Fonograma.isrc,
        Fonograma.situacao,
        Fonograma.created_at,
        User.nome.label('usuario_nome')
    ).join(User, Fonograma.user_id == User.id).order_by(Fonograma.id.desc()).all()
    
    return render_template('admin/lote/excluir.html', fonogramas=fonogramas)

@admin_bp.route('/lote/editar', methods=['GET', 'POST'])
@admin_required
def editar_lote():
    """Edição em massa de fonogramas"""
    if request.method == 'POST':
        ids_str = request.form.get('fonograma_ids', '')
        campo = request.form.get('campo', '').strip()
        valor = request.form.get('valor', '').strip()
        
        # Validações
        if not ids_str:
            flash('Nenhum fonograma selecionado.', 'warning')
            return redirect(url_for('admin.editar_lote'))
        
        if not campo:
            flash('Selecione um campo para editar.', 'warning')
            return redirect(url_for('admin.editar_lote'))
        
        # Converter string de IDs para lista
        try:
            ids = [int(id.strip()) for id in ids_str.split(',') if id.strip()]
        except ValueError:
            flash('IDs inválidos.', 'danger')
            return redirect(url_for('admin.editar_lote'))
        
        if not ids:
            flash('Nenhum fonograma selecionado.', 'warning')
            return redirect(url_for('admin.editar_lote'))
        
        # Campos permitidos para edição em lote
        campos_permitidos = ['genero', 'prod_assoc', 'assoc_gestao', 'situacao', 'versao', 'idioma', 'status_ecad']
        
        if campo not in campos_permitidos:
            flash(f'Campo "{campo}" não permitido para edição em lote.', 'danger')
            return redirect(url_for('admin.editar_lote'))
        
        editados = 0
        erros = 0
        
        try:
            for fono_id in ids:
                fonograma = Fonograma.query.get(fono_id)
                if not fonograma:
                    erros += 1
                    continue
                
                setattr(fonograma, campo, valor if valor else None)
                editados += 1
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao editar fonogramas: {str(e)}', 'danger')
            return redirect(url_for('admin.editar_lote'))
        
        if editados > 0 and erros == 0:
            flash(f'{editados} fonograma(s) atualizado(s) com sucesso!', 'success')
        elif editados > 0 and erros > 0:
            flash(f'{editados} atualizado(s), {erros} não encontrados.', 'warning')
        else:
            flash('Nenhum fonograma foi editado.', 'danger')
        
        return redirect(url_for('admin.editar_lote'))
    
    # GET - mostrar formulário
    fonogramas = Fonograma.query.order_by(Fonograma.created_at.desc()).limit(100).all()
    return render_template('admin/lote/editar.html', fonogramas=fonogramas)

# ==================== RELATÓRIOS ====================

@admin_bp.route('/relatorios')
@admin_required
def menu_relatorios():
    """Menu de relatórios"""
    return render_template('admin/relatorios/menu.html')

@admin_bp.route('/relatorios/dashboard')
@admin_required
def relatorio_dashboard():
    """Dashboard com métricas visuais"""
    dados = relatorio_service.obter_dados_dashboard()
    return render_template('admin/relatorios/dashboard.html', dados=dados)

@admin_bp.route('/relatorios/envios-periodo')
@admin_required
def relatorio_envios_periodo():
    """Relatório de envios por período"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    dados = relatorio_service.envios_por_periodo(data_inicio, data_fim)
    return render_template('admin/relatorios/envios_periodo.html', dados=dados)

@admin_bp.route('/relatorios/taxa-aprovacao')
@admin_required
def relatorio_taxa_aprovacao():
    """Relatório de taxa de aprovação"""
    dados = relatorio_service.taxa_aprovacao()
    return render_template('admin/relatorios/taxa_aprovacao.html', dados=dados)

@admin_bp.route('/relatorios/pendentes')
@admin_required
def relatorio_pendentes():
    """Fonogramas pendentes há mais tempo"""
    dados = relatorio_service.fonogramas_pendentes()
    return render_template('admin/relatorios/pendentes.html', dados=dados)

@admin_bp.route('/relatorios/por-genero')
@admin_required
def relatorio_por_genero():
    """Distribuição de fonogramas por gênero"""
    dados = relatorio_service.distribuicao_por_genero()
    return render_template('admin/relatorios/por_genero.html', dados=dados)

@admin_bp.route('/relatorios/por-produtor')
@admin_required
def relatorio_por_produtor():
    """Fonogramas por produtor"""
    dados = relatorio_service.fonogramas_por_produtor()
    return render_template('admin/relatorios/por_produtor.html', dados=dados)

@admin_bp.route('/relatorios/exportar/<tipo>')
@admin_required
def exportar_relatorio(tipo):
    """Exporta relatório para Excel"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    arquivo = relatorio_service.exportar_relatorio(tipo, data_inicio, data_fim)
    return send_file(arquivo, as_attachment=True, download_name=f'relatorio_{tipo}.xlsx')

# ==================== CONFIGURAÇÕES ====================

@admin_bp.route('/config')
@admin_required
def configuracoes():
    """Configurações do sistema"""
    return render_template('admin/config/menu.html')

@admin_bp.route('/config/usuarios')
@admin_required
def gerenciar_usuarios():
    """Gerenciamento de usuários"""
    usuarios = User.query.order_by(User.nome).all()
    return render_template('admin/config/usuarios.html', usuarios=usuarios)

@admin_bp.route('/config/usuarios/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def editar_usuario(user_id):
    """Editar usuário"""
    usuario = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.role = request.form.get('role')
        usuario.associacao = request.form.get('associacao')
        usuario.ativo = request.form.get('ativo') == 'on'
        
        if request.form.get('nova_senha'):
            usuario.set_password(request.form.get('nova_senha'))
        
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_usuarios'))
    
    return render_template('admin/config/editar_usuario.html', usuario=usuario)

@admin_bp.route('/config/enums')
@admin_required
def gerenciar_enums():
    """Visualizar enums do sistema"""
    from shared.validador import (
        VERSOES, IDIOMAS, GENEROS, FUNCOES_AUTOR, CATEGORIAS_INTERPRETE,
        TIPOS_MUSICO, ASSOCIACOES, TIPOS_LANCAMENTO, FORMATOS, SITUACOES,
        TERRITORIOS, TIPOS_EXECUCAO, PRIORIDADES, TIPOS_DOCUMENTO
    )
    
    enums = {
        'Versões': VERSOES,
        'Idiomas': IDIOMAS,
        'Gêneros': GENEROS,
        'Funções de Autor': FUNCOES_AUTOR,
        'Categorias de Intérprete': CATEGORIAS_INTERPRETE,
        'Tipos de Músico': TIPOS_MUSICO,
        'Associações': ASSOCIACOES,
        'Tipos de Lançamento': TIPOS_LANCAMENTO,
        'Formatos': FORMATOS,
        'Situações': SITUACOES,
        'Territórios': TERRITORIOS,
        'Tipos de Execução': TIPOS_EXECUCAO,
        'Prioridades': PRIORIDADES,
        'Tipos de Documento': TIPOS_DOCUMENTO,
    }
    
    return render_template('admin/config/enums.html', enums=enums)

# ==================== API JSON (para AJAX) ====================

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """API: Estatísticas para dashboard"""
    stats = relatorio_service.obter_metricas_gerais()
    return jsonify(stats)

@admin_bp.route('/api/fonogramas/buscar')
@admin_required
def api_buscar_fonogramas():
    """API: Busca de fonogramas para seleção"""
    termo = request.args.get('q', '')
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    
    query = Fonograma.query
    
    if termo:
        query = query.filter(
            db.or_(
                Fonograma.isrc.ilike(f'%{termo}%'),
                Fonograma.titulo.ilike(f'%{termo}%'),
                Fonograma.titulo_obra.ilike(f'%{termo}%')
            )
        )
    
    if status:
        query = query.filter_by(status_ecad=status)
    
    fonogramas = query.limit(limit).all()
    
    return jsonify([{
        'id': f.id,
        'isrc': f.isrc,
        'titulo': f.titulo,
        'status_ecad': f.status_ecad
    } for f in fonogramas])
