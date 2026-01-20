// Estado da aplicação ECAD
let selectedFonogramas = new Set();
let currentTab = 'envios';

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarEstatisticas();
    carregarEnvios();
    setupTabs();
    setupUpload();
    setupEventListeners();
});

// Configuração de Event Listeners
function setupEventListeners() {
    // Botão Novo Envio
    document.getElementById('btnNovoEnvio').addEventListener('click', () => {
        switchTab('selecao');
    });

    // Filtrar seleção
    document.getElementById('btnFiltrarSelecao').addEventListener('click', carregarFonogramasParaSelecao);

    // Select All
    document.getElementById('selectAllFonogramas').addEventListener('change', (e) => {
        const checkboxes = document.querySelectorAll('#selecaoTableBody input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.checked = e.target.checked;
            const id = parseInt(cb.dataset.id);
            if (e.target.checked) {
                selectedFonogramas.add(id);
            } else {
                selectedFonogramas.delete(id);
            }
        });
        atualizarContadorSelecionados();
    });

    // Gerar Arquivo
    document.getElementById('btnGerarArquivo').addEventListener('click', gerarArquivoECAD);

    // Modal
    document.getElementById('closeModalDetalhes').addEventListener('click', fecharModal);
    document.getElementById('modalDetalhes').addEventListener('click', (e) => {
        if (e.target.id === 'modalDetalhes') fecharModal();
    });
}

// Tabs
function setupTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            switchTab(tab);
        });
    });
}

function switchTab(tab) {
    currentTab = tab;

    // Atualizar botões
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });

    // Atualizar conteúdo
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tab}`);
    });

    // Carregar dados específicos da tab
    if (tab === 'selecao') {
        carregarFonogramasParaSelecao();
    }
}

// Carregar Estatísticas ECAD
async function carregarEstatisticas() {
    try {
        const response = await fetch('/api/v1/ecad/estatisticas');
        const data = await response.json();

        if (data.success) {
            const stats = data.data;
            document.getElementById('statTotal').textContent = stats.total_envios || 0;
            document.getElementById('statEnviados').textContent = stats.total_fonogramas_enviados || 0;
            document.getElementById('statAceitos').textContent = stats.por_status?.ACEITO || 0;
            document.getElementById('statRecusados').textContent = stats.por_status?.RECUSADO || 0;
            document.getElementById('statPendentes').textContent = stats.por_status?.ENVIADO || 0;
        }
    } catch (err) {
        console.error('Erro ao carregar estatísticas:', err);
    }
}

// Carregar Lista de Envios
async function carregarEnvios() {
    const tbody = document.getElementById('enviosTableBody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading">Carregando...</td></tr>';

    try {
        const response = await fetch('/api/v1/ecad/envios');
        const data = await response.json();

        if (data.success && data.data.envios && data.data.envios.length > 0) {
            tbody.innerHTML = data.data.envios.map(envio => `
                <tr>
                    <td><strong>${envio.protocolo || '-'}</strong></td>
                    <td>${formatarData(envio.data_envio)}</td>
                    <td>${envio.total_fonogramas}</td>
                    <td><span class="badge badge-${envio.status?.toLowerCase()}">${envio.status}</span></td>
                    <td class="text-success">${envio.aceitos || 0}</td>
                    <td class="text-danger">${envio.recusados || 0}</td>
                    <td>
                        <button class="btn-action btn-view" onclick="verDetalhes(${envio.id})" title="Ver Detalhes">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 2C4.5 2 1.5 4.5 0 8c1.5 3.5 4.5 6 8 6s6.5-2.5 8-6c-1.5-3.5-4.5-6-8-6zm0 10c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4z"/>
                            </svg>
                        </button>
                        <button class="btn-action btn-edit" onclick="baixarArquivo(${envio.id})" title="Baixar Arquivo">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                                <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
                            </svg>
                        </button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="empty">Nenhum envio realizado ainda</td></tr>';
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="error">Erro ao carregar: ${err.message}</td></tr>`;
    }
}

// Carregar Fonogramas para Seleção
async function carregarFonogramasParaSelecao() {
    const tbody = document.getElementById('selecaoTableBody');
    const statusFilter = document.getElementById('filtroStatusEcad').value;
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Carregando...</td></tr>';

    try {
        let url = '/api/v1/fonogramas?per_page=100';
        if (statusFilter) {
            url += `&status_ecad=${statusFilter}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success && data.data.fonogramas && data.data.fonogramas.length > 0) {
            let fonogramas = data.data.fonogramas;

            // Se houver filtro específico, aplicar
            if (statusFilter) {
                fonogramas = fonogramas.filter(f => (f.status_ecad || 'NAO_ENVIADO') === statusFilter);
            }
            // Quando 'Todos os Status' selecionado, mostrar TODOS (sem filtro)

            if (fonogramas.length > 0) {
                tbody.innerHTML = fonogramas.map(f => `
                    <tr>
                        <td>
                            <input type="checkbox" data-id="${f.id}" class="fonograma-checkbox"
                                   ${selectedFonogramas.has(f.id) ? 'checked' : ''}>
                        </td>
                        <td>${f.isrc}</td>
                        <td>${f.titulo}</td>
                        <td>${f.prod_nome || '-'}</td>
                        <td><span class="badge badge-${(f.status_ecad || 'nao_enviado').toLowerCase()}">${f.status_ecad || 'NAO_ENVIADO'}</span></td>
                        <td>${f.tentativas_envio || 0}</td>
                    </tr>
                `).join('');

                // Adicionar listeners aos checkboxes
                document.querySelectorAll('.fonograma-checkbox').forEach(cb => {
                    cb.addEventListener('change', (e) => {
                        const id = parseInt(e.target.dataset.id);
                        if (e.target.checked) {
                            selectedFonogramas.add(id);
                        } else {
                            selectedFonogramas.delete(id);
                        }
                        atualizarContadorSelecionados();
                    });
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="6" class="empty">Nenhum fonograma disponível para envio</td></tr>';
            }
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="empty">Nenhum fonograma encontrado</td></tr>';
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="error">Erro ao carregar: ${err.message}</td></tr>`;
    }
}

function atualizarContadorSelecionados() {
    const count = selectedFonogramas.size;
    document.getElementById('countSelecionados').textContent = count;
    document.getElementById('btnGerarArquivo').disabled = count === 0;
}

// Gerar Arquivo ECAD
async function gerarArquivoECAD() {
    if (selectedFonogramas.size === 0) {
        alert('Selecione pelo menos um fonograma');
        return;
    }

    const btn = document.getElementById('btnGerarArquivo');
    btn.disabled = true;
    btn.textContent = 'Gerando...';

    try {
        const response = await fetch('/api/v1/ecad/gerar-arquivo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fonograma_ids: Array.from(selectedFonogramas),
                formato: 'excel'
            })
        });

        const data = await response.json();

        if (data.success) {
            alert(`Arquivo gerado com sucesso!\nProtocolo: ${data.data.protocolo}\nFonogramas: ${data.data.total_fonogramas}`);

            // Download do arquivo
            if (data.data.arquivo) {
                window.location.href = `/outputs/${data.data.arquivo}`;
            }

            // Limpar seleção e recarregar
            selectedFonogramas.clear();
            atualizarContadorSelecionados();
            carregarEstatisticas();
            carregarEnvios();
            switchTab('envios');
        } else {
            // Verificar se há detalhes de erros de validação
            let mensagemErro = data.error || 'Erro ao gerar arquivo';

            if (data.detalhes && data.detalhes.erros && data.detalhes.erros.length > 0) {
                mensagemErro += '\n\nDetalhes dos erros:';
                data.detalhes.erros.slice(0, 5).forEach(erro => {
                    mensagemErro += `\n\n• ${erro.isrc} - ${erro.titulo}:`;
                    erro.erros.forEach(e => {
                        mensagemErro += `\n  - ${e}`;
                    });
                });
                if (data.detalhes.erros.length > 5) {
                    mensagemErro += `\n\n... e mais ${data.detalhes.erros.length - 5} fonograma(s) com erro`;
                }
            }

            throw new Error(mensagemErro);
        }
    } catch (err) {
        alert('Erro: ' + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
            </svg>
            Gerar Arquivo ECAD
        `;
    }
}

// Upload de Retorno
function setupUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('retornoFile');
    const btnSelecionar = document.getElementById('btnSelecionarRetorno');

    btnSelecionar.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect({ target: fileInput });
        }
    });

    document.getElementById('btnNovoRetorno').addEventListener('click', () => {
        document.getElementById('retornoResult').style.display = 'none';
        resetUploadArea();  // Restaura área de upload completa
        document.getElementById('uploadArea').style.display = 'flex';
    });
}

async function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        document.getElementById('uploadArea').innerHTML = `
            <div class="loading-spinner"></div>
            <p>Processando arquivo...</p>
        `;

        const response = await fetch('/api/v1/ecad/importar-retorno', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('uploadArea').style.display = 'none';
            document.getElementById('retornoResult').style.display = 'block';

            const result = data.data;
            document.getElementById('resultTotal').textContent = result.processados || 0;
            document.getElementById('resultAceitos').textContent = result.aceitos || 0;
            document.getElementById('resultRecusados').textContent = result.recusados || 0;

            carregarEstatisticas();
        } else {
            throw new Error(data.error || 'Erro ao processar arquivo');
        }
    } catch (err) {
        alert('Erro: ' + err.message);
        resetUploadArea();
    }
}

function resetUploadArea() {
    document.getElementById('uploadArea').innerHTML = `
        <svg width="48" height="48" viewBox="0 0 16 16" fill="currentColor">
            <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
            <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
        </svg>
        <h3>Importar Arquivo de Retorno ECAD</h3>
        <p>Arraste e solte o arquivo aqui ou clique para selecionar</p>
        <p class="upload-formats">Formatos aceitos: Excel (.xlsx, .xls), CSV, TXT</p>
        <input type="file" id="retornoFile" accept=".xlsx,.xls,.csv,.txt" hidden>
        <button class="btn-secondary" id="btnSelecionarRetorno">Selecionar Arquivo</button>
    `;
    setupUpload();
}

// Ver Detalhes do Envio
async function verDetalhes(envioId) {
    const modalBody = document.getElementById('modalDetalhesBody');
    modalBody.innerHTML = '<div class="loading">Carregando...</div>';
    document.getElementById('modalDetalhes').style.display = 'flex';

    try {
        const response = await fetch(`/api/v1/ecad/envios/${envioId}`);
        const data = await response.json();

        if (data.success) {
            const envio = data.data;
            modalBody.innerHTML = `
                <div class="detalhes-info">
                    <p><strong>Protocolo:</strong> ${envio.protocolo}</p>
                    <p><strong>Data:</strong> ${formatarData(envio.data_envio)}</p>
                    <p><strong>Status:</strong> <span class="badge badge-${envio.status?.toLowerCase()}">${envio.status}</span></p>
                    <p><strong>Total de Fonogramas:</strong> ${envio.total_fonogramas}</p>
                </div>
                <h4>Fonogramas do Envio</h4>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ISRC</th>
                            <th>Título</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${envio.fonogramas?.map(f => `
                            <tr>
                                <td>${f.isrc}</td>
                                <td>${f.titulo}</td>
                                <td><span class="badge badge-${f.status_ecad?.toLowerCase()}">${f.status_ecad}</span></td>
                            </tr>
                        `).join('') || '<tr><td colspan="3">Nenhum fonograma</td></tr>'}
                    </tbody>
                </table>
            `;
        }
    } catch (err) {
        modalBody.innerHTML = `<div class="error">Erro: ${err.message}</div>`;
    }
}

function baixarArquivo(envioId) {
    window.location.href = `/api/v1/ecad/envios/${envioId}/download`;
}

function fecharModal() {
    document.getElementById('modalDetalhes').style.display = 'none';
}

// Utilitários
function formatarData(dataStr) {
    if (!dataStr) return '-';
    const data = new Date(dataStr);
    return data.toLocaleDateString('pt-BR') + ' ' + data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}
