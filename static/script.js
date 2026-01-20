const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const btnRemove = document.getElementById('btnRemove');
const btnProcessar = document.getElementById('btnProcessar');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const errorsSection = document.getElementById('errorsSection');
const errorsTableBody = document.getElementById('errorsTableBody');
const btnDownload = document.getElementById('btnDownload');

let selectedFile = null;
let excelFileName = null;

// Verificar se os elementos existem antes de adicionar listeners
if (uploadArea) {
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
}
if (fileInput) fileInput.addEventListener('change', handleFileSelect);
if (btnRemove) btnRemove.addEventListener('click', handleRemoveFile);
if (btnProcessar) btnProcessar.addEventListener('click', handleProcessar);
if (btnDownload) btnDownload.addEventListener('click', handleDownload);

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    if (!file.name.toLowerCase().endsWith('.csv')) {
        alert('Por favor, selecione um arquivo CSV.');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'flex';
    btnProcessar.disabled = false;

    resultsSection.style.display = 'none';
    excelFileName = null;
}

function handleRemoveFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    btnProcessar.disabled = true;
    resultsSection.style.display = 'none';
    excelFileName = null;
}

async function handleProcessar() {
    if (!selectedFile) {
        alert('Por favor, selecione um arquivo primeiro.');
        return;
    }

    btnProcessar.disabled = true;
    btnProcessar.querySelector('.btn-text').style.display = 'none';
    btnProcessar.querySelector('.btn-loader').style.display = 'inline';
    progressSection.style.display = 'block';
    progressFill.style.width = '30%';
    progressText.textContent = 'Enviando arquivo...';

    const formData = new FormData();
    formData.append('file', selectedFile);

    // Adicionar CSRF token para proteção
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content
        || document.querySelector('input[name="csrf_token"]')?.value;
    if (csrfToken) {
        formData.append('csrf_token', csrfToken);
    }

    try {
        progressFill.style.width = '60%';
        progressText.textContent = 'Processando dados...';

        const response = await fetch(window.location.pathname, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',  // IMPORTANTE: enviar cookies de sessão
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        progressFill.style.width = '90%';
        progressText.textContent = 'Finalizando...';

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.erro || 'Erro ao processar arquivo');
        }

        progressFill.style.width = '100%';
        progressText.textContent = 'Concluído!';

        setTimeout(() => {
            exibirResultados(data);
            progressSection.style.display = 'none';
            progressFill.style.width = '0%';
        }, 500);

    } catch (error) {
        progressSection.style.display = 'none';
        alert('Erro ao processar arquivo: ' + error.message);
        console.error('Erro:', error);
    } finally {
        btnProcessar.disabled = false;
        btnProcessar.querySelector('.btn-text').style.display = 'inline';
        btnProcessar.querySelector('.btn-loader').style.display = 'none';

        // Resetar input para permitir re-upload do mesmo arquivo
        fileInput.value = '';
    }
}

function exibirResultados(data) {
    document.getElementById('statTotal').textContent = data.total_linhas || 0;
    document.getElementById('statValidas').textContent = data.linhas_validas || 0;
    document.getElementById('statErros').textContent = data.linhas_com_erro || 0;
    document.getElementById('statTotalErros').textContent = data.total_erros || 0;

    const errorsSection = document.getElementById('errorsSection');
    const errorsGrouped = document.getElementById('errorsGrouped');
    const errorsMore = document.getElementById('errorsMore');

    if (data.erros && data.erros.length > 0) {
        // Agrupar erros por linha
        const errosPorLinha = {};
        data.erros.forEach(erro => {
            const linha = erro.linha || 0;
            if (!errosPorLinha[linha]) {
                errosPorLinha[linha] = [];
            }
            errosPorLinha[linha].push(erro);
        });

        // Ordenar linhas
        const linhas = Object.keys(errosPorLinha).sort((a, b) => parseInt(a) - parseInt(b));

        // Limitar exibição inicial (máximo 10 linhas)
        const maxLinhasIniciais = 10;
        const linhasParaExibir = linhas.slice(0, maxLinhasIniciais);
        const linhasRestantes = linhas.length - maxLinhasIniciais;

        // Renderizar erros agrupados
        errorsGrouped.innerHTML = linhasParaExibir.map(linha => {
            const erros = errosPorLinha[linha];
            const isExpanded = false; // Todos começam minimizados

            return `
                <div class="error-line-group ${isExpanded ? 'expanded' : ''}">
                    <div class="error-line-header" onclick="toggleErrorLine(this)">
                        <span class="error-line-toggle">${isExpanded ? '▼' : '▶'}</span>
                        <span class="error-line-number">Linha ${linha}</span>
                        <span class="error-line-count">${erros.length} erro${erros.length > 1 ? 's' : ''}</span>
                    </div>
                    <div class="error-line-content" style="${isExpanded ? '' : 'display: none;'}">
                        ${erros.map(erro => `
                            <div class="error-item">
                                <span class="error-campo">${erro.campo || '-'}</span>
                                <span class="error-valor">${truncateText(erro.valor, 30)}</span>
                                <span class="error-msg">${erro.erro || '-'}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }).join('');

        // Mostrar botão "Mostrar mais" se houver mais linhas
        if (linhasRestantes > 0) {
            errorsMore.style.display = 'block';
            document.getElementById('errorsRemaining').textContent = `(+${linhasRestantes} linhas com erros)`;
            document.getElementById('btnShowMore').onclick = () => {
                // Adicionar mais linhas
                const linhasExtras = linhas.slice(maxLinhasIniciais);
                linhasExtras.forEach(linha => {
                    const erros = errosPorLinha[linha];
                    const div = document.createElement('div');
                    div.className = 'error-line-group';
                    div.innerHTML = `
                        <div class="error-line-header" onclick="toggleErrorLine(this)">
                            <span class="error-line-toggle">▶</span>
                            <span class="error-line-number">Linha ${linha}</span>
                            <span class="error-line-count">${erros.length} erro${erros.length > 1 ? 's' : ''}</span>
                        </div>
                        <div class="error-line-content" style="display: none;">
                            ${erros.map(erro => `
                                <div class="error-item">
                                    <span class="error-campo">${erro.campo || '-'}</span>
                                    <span class="error-valor">${truncateText(erro.valor, 30)}</span>
                                    <span class="error-msg">${erro.erro || '-'}</span>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    errorsGrouped.appendChild(div);
                });
                errorsMore.style.display = 'none';
            };
        } else {
            errorsMore.style.display = 'none';
        }

        // Adicionar eventos aos botões de expansão
        document.getElementById('btnExpandAll').onclick = () => {
            document.querySelectorAll('.error-line-group').forEach(group => {
                group.classList.add('expanded');
                group.querySelector('.error-line-toggle').textContent = '▼';
                group.querySelector('.error-line-content').style.display = 'block';
            });
        };

        document.getElementById('btnCollapseAll').onclick = () => {
            document.querySelectorAll('.error-line-group').forEach(group => {
                group.classList.remove('expanded');
                group.querySelector('.error-line-toggle').textContent = '▶';
                group.querySelector('.error-line-content').style.display = 'none';
            });
        };

        errorsSection.style.display = 'block';
    } else {
        errorsSection.style.display = 'none';
    }

    if (data.arquivo_excel) {
        excelFileName = data.arquivo_excel;
        btnDownload.style.display = 'inline-block';
    } else {
        btnDownload.style.display = 'none';
    }

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Funções auxiliares
function toggleErrorLine(header) {
    const group = header.parentElement;
    const content = group.querySelector('.error-line-content');
    const toggle = group.querySelector('.error-line-toggle');

    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.textContent = '▼';
        group.classList.add('expanded');
    } else {
        content.style.display = 'none';
        toggle.textContent = '▶';
        group.classList.remove('expanded');
    }
}

function truncateText(text, maxLen) {
    if (!text) return '-';
    text = String(text);
    return text.length > maxLen ? text.substring(0, maxLen) + '...' : text;
}

function handleDownload() {
    if (!excelFileName) {
        alert('Nenhum arquivo disponível para download.');
        return;
    }

    window.location.href = `/app/download/${excelFileName}`;
}


