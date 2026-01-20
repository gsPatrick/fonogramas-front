// Estado da aplicação
let currentPage = 1;
let perPage = 20;
let selectedIds = new Set();
let totalPages = 1;

// Elementos DOM
const tableBody = document.getElementById('fonogramasTableBody');
const pagination = document.getElementById('pagination');
const searchInput = document.getElementById('searchInput');
const situacaoFilter = document.getElementById('situacaoFilter');
const generoFilter = document.getElementById('generoFilter');
const btnFiltrar = document.getElementById('btnFiltrar');
const btnLimparFiltros = document.getElementById('btnLimparFiltros');
const selectAll = document.getElementById('selectAll');
const btnEditarLote = document.getElementById('btnEditarLote');
const btnDeletarLote = document.getElementById('btnDeletarLote');
const btnNovo = document.getElementById('btnNovo');

// Event Listeners
btnFiltrar.addEventListener('click', () => {
    currentPage = 1;
    carregarFonogramas();
});

btnLimparFiltros.addEventListener('click', () => {
    searchInput.value = '';
    situacaoFilter.value = '';
    generoFilter.value = '';
    currentPage = 1;
    carregarFonogramas();
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        currentPage = 1;
        carregarFonogramas();
    }
});

selectAll.addEventListener('change', (e) => {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][data-id]');
    checkboxes.forEach(cb => {
        cb.checked = e.target.checked;
        if (e.target.checked) {
            selectedIds.add(parseInt(cb.dataset.id));
        } else {
            selectedIds.delete(parseInt(cb.dataset.id));
        }
    });
    atualizarBotoesLote();
});

btnNovo.addEventListener('click', () => {
    window.location.href = '/fonogramas/novo';
});

btnEditarLote.addEventListener('click', () => {
    abrirModalLote();
});

btnDeletarLote.addEventListener('click', () => {
    if (confirm(`Tem certeza que deseja deletar ${selectedIds.size} fonograma(s)?`)) {
        deletarLote();
    }
});

// Carregar fonogramas
function carregarFonogramas() {
    const params = new URLSearchParams({
        page: currentPage,
        per_page: perPage
    });

    if (searchInput.value) params.append('search', searchInput.value);
    if (situacaoFilter.value) params.append('situacao', situacaoFilter.value);
    if (generoFilter.value) params.append('genero', generoFilter.value);

    tableBody.innerHTML = '<tr><td colspan="9" class="loading">Carregando...</td></tr>';

    fetch(`/api/v1/fonogramas?${params}`)
        .then(res => res.json())
        .then(response => {
            if (!response.success) {
                throw new Error(response.error || 'Erro ao carregar fonogramas');
            }
            const data = response.data;
            totalPages = data.pagination.pages;
            renderizarTabela(data.fonogramas);
            renderizarPaginacao(data.pagination);
        })
        .catch(err => {
            tableBody.innerHTML = `<tr><td colspan="9" class="error">Erro ao carregar: ${err.message}</td></tr>`;
        });
}

function renderizarTabela(fonogramas) {
    if (fonogramas.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="9" class="empty">Nenhum fonograma encontrado</td></tr>';
        return;
    }

    tableBody.innerHTML = fonogramas.map(f => `
        <tr>
            <td><input type="checkbox" data-id="${f.id}" class="row-checkbox"></td>
            <td>${f.isrc || '-'}</td>
            <td>${f.titulo || '-'}</td>
            <td>${f.titulo_obra || '-'}</td>
            <td>${f.genero || '-'}</td>
            <td>${f.prod_nome || '-'}</td>
            <td><span class="badge badge-${f.situacao?.toLowerCase() || 'ativo'}">${f.situacao || 'ATIVO'}</span></td>
            <td>${f.created_at ? new Date(f.created_at).toLocaleDateString('pt-BR') : '-'}</td>
            <td class="actions-cell">
                <button class="btn-action btn-view" onclick="visualizarFonograma(${f.id})" title="Visualizar">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 2C4.5 2 1.5 4.5 0 8c1.5 3.5 4.5 6 8 6s6.5-2.5 8-6c-1.5-3.5-4.5-6-8-6zm0 10c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4zm0-6.5c-1.4 0-2.5 1.1-2.5 2.5s1.1 2.5 2.5 2.5 2.5-1.1 2.5-2.5-1.1-2.5-2.5-2.5z"/>
                    </svg>
                </button>
                <button class="btn-action btn-edit" onclick="editarFonograma(${f.id})" title="Editar">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
                    </svg>
                </button>
                <button class="btn-action btn-delete" onclick="deletarFonograma(${f.id})" title="Deletar">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                        <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                    </svg>
                </button>
            </td>
        </tr>
    `).join('');

    // Adiciona listeners aos checkboxes
    document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.addEventListener('change', (e) => {
            const id = parseInt(e.target.dataset.id);
            if (e.target.checked) {
                selectedIds.add(id);
            } else {
                selectedIds.delete(id);
                selectAll.checked = false;
            }
            atualizarBotoesLote();
        });
    });
}

function renderizarPaginacao(pagination) {
    if (totalPages <= 1) {
        document.getElementById('pagination').innerHTML = '';
        return;
    }

    let html = '<div class="pagination-controls">';

    // Botão Anterior
    if (currentPage > 1) {
        html += `<button class="btn-pagination" onclick="irParaPagina(${currentPage - 1})">« Anterior</button>`;
    }

    // Números de página
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        html += `<button class="btn-pagination ${i === currentPage ? 'active' : ''}" onclick="irParaPagina(${i})">${i}</button>`;
    }

    // Botão Próximo
    if (currentPage < totalPages) {
        html += `<button class="btn-pagination" onclick="irParaPagina(${currentPage + 1})">Próximo »</button>`;
    }

    html += `</div><div class="pagination-info">Página ${currentPage} de ${totalPages} (${pagination.total} total)</div>`;
    document.getElementById('pagination').innerHTML = html;
}

function irParaPagina(page) {
    currentPage = page;
    carregarFonogramas();
}

function visualizarFonograma(id) {
    window.location.href = `/fonogramas/${id}`;
}

function editarFonograma(id) {
    window.location.href = `/fonogramas/${id}/editar`;
}

function deletarFonograma(id) {
    if (confirm('Tem certeza que deseja deletar este fonograma?')) {
        fetch(`/api/v1/fonogramas/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                alert('Fonograma deletado com sucesso!');
                carregarFonogramas();
            })
            .catch(err => {
                alert('Erro ao deletar: ' + err.message);
            });
    }
}

function atualizarBotoesLote() {
    const count = selectedIds.size;
    btnEditarLote.disabled = count === 0;
    btnDeletarLote.disabled = count === 0;
}

function abrirModalLote() {
    document.getElementById('countSelecionados').textContent = selectedIds.size;
    document.getElementById('modalLote').style.display = 'flex';
}

function fecharModalLote() {
    document.getElementById('modalLote').style.display = 'none';
    document.getElementById('campoLote').value = 'situacao';
    document.getElementById('valorLote').value = '';
}

function deletarLote() {
    fetch('/api/v1/fonogramas/lote', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: Array.from(selectedIds) })
    })
        .then(res => res.json())
        .then(response => {
            if (!response.success) {
                throw new Error(response.error || 'Erro ao deletar');
            }
            alert(response.message || `${response.data.deletados} fonograma(s) deletado(s)`);
            selectedIds.clear();
            selectAll.checked = false;
            atualizarBotoesLote();
            carregarFonogramas();
        })
        .catch(err => {
            alert('Erro ao deletar: ' + err.message);
        });
}

// Modal listeners
document.getElementById('closeModalLote').addEventListener('click', fecharModalLote);
document.getElementById('cancelModalLote').addEventListener('click', fecharModalLote);
document.getElementById('saveModalLote').addEventListener('click', () => {
    const campo = document.getElementById('campoLote').value;
    const valor = document.getElementById('valorLote').value;

    if (!valor) {
        alert('Por favor, informe o novo valor');
        return;
    }

    fetch('/api/v1/fonogramas/lote', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ids: Array.from(selectedIds),
            campos: { [campo]: valor }
        })
    })
        .then(res => res.json())
        .then(response => {
            if (!response.success) {
                throw new Error(response.error || 'Erro ao atualizar');
            }
            alert(response.message || `${response.data.atualizados} fonograma(s) atualizado(s)`);
            fecharModalLote();
            selectedIds.clear();
            selectAll.checked = false;
            atualizarBotoesLote();
            carregarFonogramas();
        })
        .catch(err => {
            alert('Erro ao atualizar: ' + err.message);
        });
});

// Fechar modal ao clicar fora
document.getElementById('modalLote').addEventListener('click', (e) => {
    if (e.target.id === 'modalLote') {
        fecharModalLote();
    }
});

// Carregar ao iniciar
carregarFonogramas();



