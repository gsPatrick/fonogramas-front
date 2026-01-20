// Estado
let autores = [];
let editoras = [];
let interpretes = [];
let musicos = [];
let documentos = [];

// Elementos
const form = document.getElementById('fonogramaForm');
const btnSalvar = document.getElementById('btnSalvar');

// Carregar dados se estiver editando
if (fonogramaId) {
    carregarFonograma(fonogramaId);
}

// Event Listeners
btnSalvar.addEventListener('click', salvarFonograma);

// Funções de carregamento
async function carregarFonograma(id) {
    try {
        const res = await fetch(`/api/v1/fonogramas/${id}`);
        const response = await res.json();

        if (!response.success) {
            throw new Error(response.error || 'Erro ao carregar fonograma');
        }

        preencherFormulario(response.data);
    } catch (err) {
        alert('Erro ao carregar fonograma: ' + err.message);
    }
}

function preencherFormulario(data) {
    // Campos básicos
    document.getElementById('isrc').value = data.isrc || '';
    document.getElementById('titulo').value = data.titulo || '';
    document.getElementById('versao').value = data.versao || '';
    document.getElementById('duracao').value = data.duracao || '';
    document.getElementById('ano_grav').value = data.ano_grav || '';
    document.getElementById('ano_lanc').value = data.ano_lanc || '';
    document.getElementById('idioma').value = data.idioma || '';
    document.getElementById('genero').value = data.genero || '';
    document.getElementById('cod_interno').value = data.cod_interno || '';
    document.getElementById('titulo_obra').value = data.titulo_obra || '';
    document.getElementById('cod_obra').value = data.cod_obra || '';
    document.getElementById('prod_nome').value = data.prod_nome || '';
    document.getElementById('prod_doc').value = data.prod_doc || '';
    document.getElementById('prod_fantasia').value = data.prod_fantasia || '';
    document.getElementById('prod_endereco').value = data.prod_endereco || '';
    document.getElementById('prod_perc').value = data.prod_perc || '';
    document.getElementById('prod_assoc').value = data.prod_assoc || '';
    document.getElementById('prod_data_ini').value = data.prod_data_ini || '';
    document.getElementById('tipo_lanc').value = data.tipo_lanc || '';
    document.getElementById('album').value = data.album || '';
    document.getElementById('faixa').value = data.faixa || '';
    document.getElementById('selo').value = data.selo || '';
    document.getElementById('formato').value = data.formato || '';
    document.getElementById('pais').value = data.pais || '';
    document.getElementById('data_lanc').value = data.data_lanc || '';
    document.getElementById('assoc_gestao').value = data.assoc_gestao || '';
    document.getElementById('data_cad').value = data.data_cad || '';
    document.getElementById('situacao').value = data.situacao || 'ATIVO';
    document.getElementById('obs_juridicas').value = data.obs_juridicas || '';
    document.getElementById('historico').value = data.historico || '';
    document.getElementById('territorio').value = data.territorio || '';
    document.getElementById('tipos_exec').value = data.tipos_exec || '';
    document.getElementById('prioridade').value = data.prioridade || '';
    document.getElementById('cod_ecad').value = data.cod_ecad || '';

    // Relacionamentos
    autores = data.autores || [];
    editoras = data.editoras || [];
    interpretes = data.interpretes || [];
    musicos = data.musicos || [];
    documentos = data.documentos || [];

    renderizarAutores();
    renderizarEditoras();
    renderizarInterpretes();
    renderizarMusicos();
    renderizarDocumentos();
}

// Funções de renderização
function renderizarAutores() {
    const container = document.getElementById('autoresContainer');
    container.innerHTML = autores.map((autor, idx) => `
        <div class="item-row" data-idx="${idx}">
            <input type="text" placeholder="Nome" value="${autor.nome || ''}" onchange="atualizarAutor(${idx}, 'nome', this.value)">
            <input type="text" placeholder="CPF" value="${autor.cpf || ''}" onchange="atualizarAutor(${idx}, 'cpf', this.value)">
            <select onchange="atualizarAutor(${idx}, 'funcao', this.value)">
                <option value="">Função</option>
                <option value="COMPOSITOR" ${autor.funcao === 'COMPOSITOR' ? 'selected' : ''}>Compositor</option>
                <option value="LETRISTA" ${autor.funcao === 'LETRISTA' ? 'selected' : ''}>Letrista</option>
                <option value="COMPOSITOR_LETRISTA" ${autor.funcao === 'COMPOSITOR_LETRISTA' ? 'selected' : ''}>Compositor/Letrista</option>
                <option value="VERSIONISTA" ${autor.funcao === 'VERSIONISTA' ? 'selected' : ''}>Versionista</option>
                <option value="ADAPTADOR" ${autor.funcao === 'ADAPTADOR' ? 'selected' : ''}>Adaptador</option>
            </select>
            <input type="number" placeholder="%" value="${autor.percentual || ''}" step="0.01" onchange="atualizarAutor(${idx}, 'percentual', parseFloat(this.value))">
            <button type="button" class="btn-remove-item" onclick="removerAutor(${idx})">×</button>
        </div>
    `).join('');
}

function renderizarEditoras() {
    const container = document.getElementById('editorasContainer');
    container.innerHTML = editoras.map((editora, idx) => `
        <div class="item-row" data-idx="${idx}">
            <input type="text" placeholder="Nome" value="${editora.nome || ''}" onchange="atualizarEditora(${idx}, 'nome', this.value)">
            <input type="text" placeholder="CNPJ" value="${editora.cnpj || ''}" onchange="atualizarEditora(${idx}, 'cnpj', this.value)">
            <input type="number" placeholder="%" value="${editora.percentual || ''}" step="0.01" onchange="atualizarEditora(${idx}, 'percentual', parseFloat(this.value))">
            <button type="button" class="btn-remove-item" onclick="removerEditora(${idx})">×</button>
        </div>
    `).join('');
}

function renderizarInterpretes() {
    const container = document.getElementById('interpretesContainer');
    container.innerHTML = interpretes.map((interprete, idx) => `
        <div class="item-row" data-idx="${idx}">
            <input type="text" placeholder="Nome" value="${interprete.nome || ''}" onchange="atualizarInterprete(${idx}, 'nome', this.value)">
            <input type="text" placeholder="CPF/CNPJ" value="${interprete.doc || ''}" onchange="atualizarInterprete(${idx}, 'doc', this.value)">
            <select onchange="atualizarInterprete(${idx}, 'categoria', this.value)">
                <option value="">Categoria</option>
                <option value="PRINCIPAL" ${interprete.categoria === 'PRINCIPAL' ? 'selected' : ''}>Principal</option>
                <option value="COADJUVANTE" ${interprete.categoria === 'COADJUVANTE' ? 'selected' : ''}>Coadjuvante</option>
                <option value="PARTICIPACAO_ESPECIAL" ${interprete.categoria === 'PARTICIPACAO_ESPECIAL' ? 'selected' : ''}>Participação Especial</option>
            </select>
            <input type="number" placeholder="%" value="${interprete.percentual || ''}" step="0.01" onchange="atualizarInterprete(${idx}, 'percentual', parseFloat(this.value))">
            <select onchange="atualizarInterprete(${idx}, 'associacao', this.value)">
                <option value="">Associação</option>
                <option value="ABRAMUS" ${interprete.associacao === 'ABRAMUS' ? 'selected' : ''}>ABRAMUS</option>
                <option value="UBC" ${interprete.associacao === 'UBC' ? 'selected' : ''}>UBC</option>
                <option value="AMAR" ${interprete.associacao === 'AMAR' ? 'selected' : ''}>AMAR</option>
                <option value="SBACEM" ${interprete.associacao === 'SBACEM' ? 'selected' : ''}>SBACEM</option>
                <option value="SICAM" ${interprete.associacao === 'SICAM' ? 'selected' : ''}>SICAM</option>
                <option value="SOCINPRO" ${interprete.associacao === 'SOCINPRO' ? 'selected' : ''}>SOCINPRO</option>
                <option value="ASSIM" ${interprete.associacao === 'ASSIM' ? 'selected' : ''}>ASSIM</option>
                <option value="SADEMBRA" ${interprete.associacao === 'SADEMBRA' ? 'selected' : ''}>SADEMBRA</option>
                <option value="ANACIM" ${interprete.associacao === 'ANACIM' ? 'selected' : ''}>ANACIM</option>
            </select>
            <button type="button" class="btn-remove-item" onclick="removerInterprete(${idx})">×</button>
        </div>
    `).join('');
}

function renderizarMusicos() {
    const container = document.getElementById('musicosContainer');
    container.innerHTML = musicos.map((musico, idx) => `
        <div class="item-row" data-idx="${idx}">
            <input type="text" placeholder="Nome" value="${musico.nome || ''}" onchange="atualizarMusico(${idx}, 'nome', this.value)">
            <input type="text" placeholder="CPF" value="${musico.cpf || ''}" onchange="atualizarMusico(${idx}, 'cpf', this.value)">
            <input type="text" placeholder="Instrumento" value="${musico.instrumento || ''}" onchange="atualizarMusico(${idx}, 'instrumento', this.value)">
            <select onchange="atualizarMusico(${idx}, 'tipo', this.value)">
                <option value="">Tipo</option>
                <option value="FIXO" ${musico.tipo === 'FIXO' ? 'selected' : ''}>Fixo</option>
                <option value="EVENTUAL" ${musico.tipo === 'EVENTUAL' ? 'selected' : ''}>Eventual</option>
            </select>
            <input type="number" placeholder="%" value="${musico.percentual || ''}" step="0.01" onchange="atualizarMusico(${idx}, 'percentual', parseFloat(this.value))">
            <button type="button" class="btn-remove-item" onclick="removerMusico(${idx})">×</button>
        </div>
    `).join('');
}

function renderizarDocumentos() {
    const container = document.getElementById('documentosContainer');
    container.innerHTML = documentos.map((doc, idx) => `
        <div class="item-row" data-idx="${idx}">
            <select onchange="atualizarDocumento(${idx}, 'tipo', this.value)">
                <option value="">Tipo</option>
                <option value="DECLARACAO" ${doc.tipo === 'DECLARACAO' ? 'selected' : ''}>Declaração</option>
                <option value="CONTRATO_CESSAO" ${doc.tipo === 'CONTRATO_CESSAO' ? 'selected' : ''}>Contrato de Cessão</option>
                <option value="AUTORIZACAO_NOME" ${doc.tipo === 'AUTORIZACAO_NOME' ? 'selected' : ''}>Autorização de Nome</option>
                <option value="CONTRATO_INTERPRETE" ${doc.tipo === 'CONTRATO_INTERPRETE' ? 'selected' : ''}>Contrato de Intérprete</option>
                <option value="COMPROVANTE_ISRC" ${doc.tipo === 'COMPROVANTE_ISRC' ? 'selected' : ''}>Comprovante ISRC</option>
                <option value="OUTRO" ${doc.tipo === 'OUTRO' ? 'selected' : ''}>Outro</option>
            </select>
            <input type="text" placeholder="Referência" value="${doc.referencia || ''}" onchange="atualizarDocumento(${idx}, 'referencia', this.value)">
            <input type="text" placeholder="Data (dd/mm/yyyy)" value="${doc.data || ''}" onchange="atualizarDocumento(${idx}, 'data', this.value)">
            <button type="button" class="btn-remove-item" onclick="removerDocumento(${idx})">×</button>
        </div>
    `).join('');
}

// Funções de adicionar
function adicionarAutor() {
    autores.push({ nome: '', cpf: '', funcao: '', percentual: 0 });
    renderizarAutores();
}

function adicionarEditora() {
    editoras.push({ nome: '', cnpj: '', percentual: 0 });
    renderizarEditoras();
}

function adicionarInterprete() {
    interpretes.push({ nome: '', doc: '', categoria: '', percentual: 0, associacao: '' });
    renderizarInterpretes();
}

function adicionarMusico() {
    musicos.push({ nome: '', cpf: '', instrumento: '', tipo: '', percentual: 0 });
    renderizarMusicos();
}

function adicionarDocumento() {
    documentos.push({ tipo: '', referencia: '', data: '' });
    renderizarDocumentos();
}

// Funções de atualizar
function atualizarAutor(idx, campo, valor) {
    if (!autores[idx]) autores[idx] = {};
    autores[idx][campo] = valor;
}

function atualizarEditora(idx, campo, valor) {
    if (!editoras[idx]) editoras[idx] = {};
    editoras[idx][campo] = valor;
}

function atualizarInterprete(idx, campo, valor) {
    if (!interpretes[idx]) interpretes[idx] = {};
    interpretes[idx][campo] = valor;
}

function atualizarMusico(idx, campo, valor) {
    if (!musicos[idx]) musicos[idx] = {};
    musicos[idx][campo] = valor;
}

function atualizarDocumento(idx, campo, valor) {
    if (!documentos[idx]) documentos[idx] = {};
    documentos[idx][campo] = valor;
}

// Funções de remover
function removerAutor(idx) {
    autores.splice(idx, 1);
    renderizarAutores();
}

function removerEditora(idx) {
    editoras.splice(idx, 1);
    renderizarEditoras();
}

function removerInterprete(idx) {
    interpretes.splice(idx, 1);
    renderizarInterpretes();
}

function removerMusico(idx) {
    musicos.splice(idx, 1);
    renderizarMusicos();
}

function removerDocumento(idx) {
    documentos.splice(idx, 1);
    renderizarDocumentos();
}

// Salvar
async function salvarFonograma() {
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Validações básicas
    if (autores.length === 0) {
        alert('Adicione pelo menos um autor');
        return;
    }

    if (interpretes.length === 0) {
        alert('Adicione pelo menos um intérprete');
        return;
    }

    const data = {
        isrc: document.getElementById('isrc').value.trim(),
        titulo: document.getElementById('titulo').value.trim(),
        versao: document.getElementById('versao').value || null,
        duracao: document.getElementById('duracao').value.trim(),
        ano_grav: document.getElementById('ano_grav').value || null,
        ano_lanc: parseInt(document.getElementById('ano_lanc').value),
        idioma: document.getElementById('idioma').value || null,
        genero: document.getElementById('genero').value.trim(),
        cod_interno: document.getElementById('cod_interno').value.trim() || null,
        titulo_obra: document.getElementById('titulo_obra').value.trim(),
        cod_obra: document.getElementById('cod_obra').value.trim() || null,
        prod_nome: document.getElementById('prod_nome').value.trim(),
        prod_doc: document.getElementById('prod_doc').value.trim(),
        prod_fantasia: document.getElementById('prod_fantasia').value.trim() || null,
        prod_endereco: document.getElementById('prod_endereco').value.trim() || null,
        prod_perc: parseFloat(document.getElementById('prod_perc').value),
        prod_assoc: document.getElementById('prod_assoc').value || null,
        prod_data_ini: document.getElementById('prod_data_ini').value.trim() || null,
        tipo_lanc: document.getElementById('tipo_lanc').value || null,
        album: document.getElementById('album').value.trim() || null,
        faixa: document.getElementById('faixa').value || null,
        selo: document.getElementById('selo').value.trim() || null,
        formato: document.getElementById('formato').value || null,
        pais: document.getElementById('pais').value.trim() || null,
        data_lanc: document.getElementById('data_lanc').value.trim() || null,
        assoc_gestao: document.getElementById('assoc_gestao').value || null,
        data_cad: document.getElementById('data_cad').value.trim() || null,
        situacao: document.getElementById('situacao').value,
        obs_juridicas: document.getElementById('obs_juridicas').value.trim() || null,
        historico: document.getElementById('historico').value.trim() || null,
        territorio: document.getElementById('territorio').value || null,
        tipos_exec: document.getElementById('tipos_exec').value || null,
        prioridade: document.getElementById('prioridade').value || null,
        cod_ecad: document.getElementById('cod_ecad').value.trim() || null,
        autores: autores,
        editoras: editoras,
        interpretes: interpretes,
        musicos: musicos,
        documentos: documentos
    };

    btnSalvar.disabled = true;
    btnSalvar.textContent = 'Salvando...';

    try {
        const url = fonogramaId ? `/api/v1/fonogramas/${fonogramaId}` : '/api/v1/fonogramas';
        const method = fonogramaId ? 'PUT' : 'POST';

        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (!res.ok) {
            throw new Error(result.erro || 'Erro ao salvar');
        }

        alert('Fonograma salvo com sucesso!');
        window.location.href = '/fonogramas';
    } catch (err) {
        alert('Erro ao salvar: ' + err.message);
        btnSalvar.disabled = false;
        btnSalvar.textContent = 'Salvar';
    }
}

// Inicializar com pelo menos um autor e intérprete
if (!fonogramaId) {
    adicionarAutor();
    adicionarInterprete();
}



