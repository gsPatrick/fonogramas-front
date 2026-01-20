# usuario/routes.py
import os
from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for, session
from flask_login import current_user
from shared.decorators import usuario_required
from models import db, Fonograma
from usuario.services import fonograma_service, upload_service, export_service
from . import usuario_bp

# ==================== DASHBOARD ====================

@usuario_bp.route('/')
@usuario_required
def dashboard():
    """Dashboard do usuário"""
    stats = fonograma_service.obter_estatisticas_usuario(current_user)
    recentes = fonograma_service.obter_fonogramas_recentes(current_user, limit=10)
    return render_template('usuario/dashboard.html', stats=stats, recentes=recentes)

# ==================== FONOGRAMAS ====================

@usuario_bp.route('/fonogramas')
@usuario_required
def listar_fonogramas():
    """Lista fonogramas do usuário"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    busca = request.args.get('busca', '')
    genero = request.args.get('genero')
    
    fonogramas = fonograma_service.listar_fonogramas(
        usuario=current_user,
        page=page,
        per_page=per_page,
        busca=busca,
        genero=genero
    )
    
    return render_template('usuario/fonogramas/lista.html', fonogramas=fonogramas)

@usuario_bp.route('/fonogramas/novo', methods=['GET', 'POST'])
@usuario_required
def novo_fonograma():
    """Criar novo fonograma manualmente"""
    if request.method == 'POST':
        dados = request.form.to_dict()
        resultado = fonograma_service.criar_fonograma(dados, current_user)
        
        if resultado['sucesso']:
            flash('Fonograma criado com sucesso!', 'success')
            return redirect(url_for('usuario.detalhes_fonograma', fonograma_id=resultado['fonograma_id']))
        else:
            flash(f'Erro: {resultado["erro"]}', 'danger')
            return render_template('usuario/fonogramas/novo.html', dados=dados, erros=resultado.get('erros', []))
    
    return render_template('usuario/fonogramas/novo.html')

@usuario_bp.route('/fonogramas/<int:fonograma_id>')
@usuario_required
def detalhes_fonograma(fonograma_id):
    """Detalhes de um fonograma"""
    fonograma = fonograma_service.obter_fonograma(fonograma_id, current_user)
    if not fonograma:
        flash('Fonograma não encontrado.', 'danger')
        return redirect(url_for('usuario.listar_fonogramas'))
    
    # Status simplificado (sem detalhes técnicos)
    status_display = fonograma_service.obter_status_simplificado(fonograma)
    
    return render_template('usuario/fonogramas/detalhes.html', 
                         fonograma=fonograma, 
                         status_display=status_display)

@usuario_bp.route('/fonogramas/<int:fonograma_id>/editar', methods=['GET', 'POST'])
@usuario_required
def editar_fonograma(fonograma_id):
    """Editar fonograma"""
    fonograma = fonograma_service.obter_fonograma(fonograma_id, current_user)
    if not fonograma:
        flash('Fonograma não encontrado.', 'danger')
        return redirect(url_for('usuario.listar_fonogramas'))
    
    # Não permitir edição se já foi enviado/aceito
    if fonograma.status_ecad in ['ENVIADO', 'ACEITO']:
        flash('Fonograma já enviado ao ECAD não pode ser editado.', 'warning')
        return redirect(url_for('usuario.detalhes_fonograma', fonograma_id=fonograma_id))
    
    if request.method == 'POST':
        dados = request.form.to_dict()
        resultado = fonograma_service.atualizar_fonograma(fonograma, dados, current_user)
        
        if resultado['sucesso']:
            flash('Fonograma atualizado com sucesso!', 'success')
            return redirect(url_for('usuario.detalhes_fonograma', fonograma_id=fonograma_id))
        else:
            flash(f'Erro: {resultado["erro"]}', 'danger')
    
    return render_template('usuario/fonogramas/editar.html', fonograma=fonograma)

@usuario_bp.route('/fonogramas/<int:fonograma_id>/excluir', methods=['POST'])
@usuario_required
def excluir_fonograma(fonograma_id):
    """Excluir fonograma"""
    fonograma = fonograma_service.obter_fonograma(fonograma_id, current_user)
    if not fonograma:
        flash('Fonograma não encontrado.', 'danger')
        return redirect(url_for('usuario.listar_fonogramas'))
    
    # Não permitir exclusão se já foi enviado
    if fonograma.status_ecad in ['ENVIADO', 'ACEITO']:
        flash('Fonograma já enviado ao ECAD não pode ser excluído.', 'warning')
        return redirect(url_for('usuario.detalhes_fonograma', fonograma_id=fonograma_id))
    
    resultado = fonograma_service.excluir_fonograma(fonograma, current_user)
    
    if resultado['sucesso']:
        flash('Fonograma excluído com sucesso!', 'success')
    else:
        flash(f'Erro: {resultado["erro"]}', 'danger')
    
    return redirect(url_for('usuario.listar_fonogramas'))

# ==================== UPLOAD ====================

@usuario_bp.route('/upload', methods=['GET', 'POST'])
@usuario_required
def upload_arquivo():
    """Upload de arquivo para validação"""
    if request.method == 'POST':
        if 'arquivo' not in request.files and 'file' not in request.files:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
                return jsonify({'erro': 'Nenhum arquivo enviado'}), 400
            flash('Nenhum arquivo enviado.', 'danger')
            return redirect(request.url)
        
        arquivo = request.files.get('arquivo') or request.files.get('file')
        
        # Detecção de AJAX/Fetch do script.js
        # O script.js original envia via fetch. Vamos detectar se espera JSON.
        # Mas para garantir, vamos ver se o campo 'file' (usado pelo script.js) está presente
        is_ajax = 'file' in request.files or request.path.endswith('/upload') # script.js usa /upload se ajustarmos
        
        if is_ajax:
            # Modo API para o Conversor (script.js)
            try:
                if not arquivo.filename.lower().endswith('.csv'):
                     return jsonify({'erro': 'Apenas arquivos CSV são aceitos para conversão.'}), 400

                resultado = upload_service.processar_para_frontend(arquivo)
                
                # IMPORTANTE: Salvar dados VALIDADOS na sessão para o botão "Salvar no Dashboard"
                # Agora salvamos os dados brutos validados diretamente, não o caminho do arquivo
                session['upload_resultado'] = {
                    'arquivo_temp': resultado.get('arquivo_temp'),
                    'dados_validados': resultado.get('dados_validados', [])  # Lista de dicts com dados originais
                }
                session.modified = True  # Forçar persistência da sessão
                
                return jsonify(resultado)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'erro': str(e)}), 500

        # Modo Clássico (Formulário Padrão - Mantendo compatibilidade se necessário)
        resultado = upload_service.validar_arquivo(arquivo)
        session['upload_resultado'] = resultado
        return render_template('usuario/upload/resultado.html', resultado=resultado)
    
    return render_template('usuario/upload/form.html')

@usuario_bp.route('/download/<filename>')
@usuario_required
def download_arquivo(filename):
    """Download de arquivos gerados (Excel do conversor)"""
    try:
        # Assumindo que os arquivos estão na pasta 'outputs' na raiz do app
        output_dir = os.path.join(os.getcwd(), 'outputs')
        filepath = os.path.join(output_dir, filename)
        
        # Garantir que o nome do arquivo tenha extensão .xlsx
        download_name = filename if filename.endswith('.xlsx') else f'{filename}.xlsx'
        
        return send_file(
            filepath, 
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Erro ao baixar arquivo: {str(e)}', 'danger')
        return redirect(url_for('usuario.upload_arquivo'))

@usuario_bp.route('/upload/salvar', methods=['POST'])
@usuario_required
def salvar_upload():
    """Salvar fonogramas validados"""
    resultado_validacao = session.get('upload_resultado')
    
    if not resultado_validacao:
        flash('Sessão expirada. Faça o upload novamente.', 'warning')
        return redirect(url_for('usuario.upload_arquivo'))
    
    # Filtrar apenas linhas válidas
    salvar_apenas_validos = request.form.get('salvar_apenas_validos') == 'on'
    
    resultado = upload_service.salvar_fonogramas(
        resultado_validacao,
        current_user,
        salvar_apenas_validos=salvar_apenas_validos
    )
    
    if resultado['sucesso']:
        flash(f'Salvos: {resultado["salvos"]}, Atualizados: {resultado["atualizados"]}', 'success')
        session.pop('upload_resultado', None)
        return redirect(url_for('usuario.listar_fonogramas'))
    else:
        flash(f'Erro: {resultado["erro"]}', 'danger')
        return redirect(url_for('usuario.upload_arquivo'))

@usuario_bp.route('/upload/template')
@usuario_required
def download_template():
    """Download do template de importação"""
    arquivo = upload_service.gerar_template()
    return send_file(arquivo, as_attachment=True, download_name='template_fonogramas.xlsx')

# ==================== EXPORTAÇÃO ====================

@usuario_bp.route('/exportar', methods=['GET', 'POST'])
@usuario_required
def exportar():
    """Exportar fonogramas para Excel"""
    if request.method == 'POST':
        fonograma_ids = request.form.getlist('fonograma_ids')
        
        if not fonograma_ids:
            # Exportar todos os fonogramas do usuário
            fonograma_ids = None
        
        arquivo = export_service.exportar_fonogramas(
            usuario=current_user,
            fonograma_ids=fonograma_ids
        )
        
        return send_file(arquivo, as_attachment=True, download_name='fonogramas.xlsx')
    
    fonogramas = fonograma_service.listar_todos_fonogramas(current_user)
    return render_template('usuario/exportar/selecao.html', fonogramas=fonogramas)

# ==================== MEU HISTÓRICO ====================

@usuario_bp.route('/historico')
@usuario_required
def meu_historico():
    """Histórico de alterações do usuário"""
    page = request.args.get('page', 1, type=int)
    
    historico = fonograma_service.obter_historico_usuario(current_user, page=page)
    
    return render_template('usuario/historico/lista.html', historico=historico)

# ==================== API JSON ====================

@usuario_bp.route('/api/fonogramas/<int:fonograma_id>/status')
@usuario_required
def api_status_fonograma(fonograma_id):
    """API: Status simplificado do fonograma"""
    fonograma = fonograma_service.obter_fonograma(fonograma_id, current_user)
    if not fonograma:
        return jsonify({'erro': 'Não encontrado'}), 404
    
    status = fonograma_service.obter_status_simplificado(fonograma)
    return jsonify(status)

@usuario_bp.route('/api/validar-campo', methods=['POST'])
@usuario_required
def api_validar_campo():
    """API: Validação de campo individual (para formulário)"""
    campo = request.json.get('campo')
    valor = request.json.get('valor')
    
    resultado = upload_service.validar_campo_individual(campo, valor)
    return jsonify(resultado)
