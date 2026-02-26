# Relatório Completo: Sistema de Importação de Fonogramas (Ponta a Ponta)

## 1. Visão Geral da Arquitetura
O sistema "Importação de Fonogramas" é uma aplicação monolítica construída em **Python (Flask)** com renderização do lado do servidor via **Jinja2** (Templates HTML genéricos + Bootstrap) e que fornece também uma API REST moderna e documentada para o sistema. A persistência é gerenciada com **SQLAlchemy** (um banco SQLite por padrão `instance/fonogramas.db` configurável via URL `.env`) e o controle de migrações e sessões seguras usando Flask-Login e JWT para comunicação com o Single Sign-On (SSO) remoto. 

As principais funcionalidades gravitam ao redor do **ciclo de vida do Fonograma** e de sua submissão periódica de arquivos (Textos Posicionais Fixos ou Excel Especializado) através de "lotes" processados e submetidos à Associação (ECAD/Sbacem).

## 2. Modelagem de Dados (Banco de Dados)
O arquivo `models.py` estabelece o núcleo das estruturas de dados do sistema e dos direitos conexos.

* **Conceito de Acessos & Autenticação:**
  * `User`: Gerencia Usuários (email, senha, cargos: `admin` e `usuario`, status, token de reset). Inclui regras específicas de login automático (SSO) derivado do cookie do portal matriz (`satellite_session`).
* **Entidades Musicais (Fonograma + Partes Interessadas):**
  * `Fonograma`: É a entidade central com diversos meta-dados: Identificação (ISRC, Título, Duração, etc), Obra Musical, País de origem e Lançamento, Histórico e controle do ECAD (`status_ecad` - PENDENTE, SELECIONADO, ENVIADO, ACEITO, RECUSADO).
  * *Relacionamentos em Correntes (1-N com Fonograma):* 
    * `Autor`: Compositor, Letrista (com % e documento validado).
    * `Editora`: % de edição da Obra por ente jurídico.
    * `Interprete` (Principal/Coadjuvante), `Musico` (Fixo/Eventual).
    * `Documento` (Links ou referências para Declarações, Contratos).
* **Auditoria e Monitoramento ECAD:**
  * `HistoricoFonograma`: Logs detalhados imutáveis; grava o tipo, valor antigo e valor novo a cada salvamento das edições, para segurança do ISRC.
  * `EnvioECAD` & `RetornoECAD` (Relacionamento N-N com a tabela combinada `fonograma_envio`): Guardam o sumário lógico dos protocolos gerados para comunicação, o resultado final (processado/erros), e o laudo de rastreio de retorno para cada submissão (Recusado/Aceito por item).

## 3. O Frontend (Views, Modulos e Assets)
Renderizado usando HTML limpo e prático (`render_template`), dividido estruturalmente em três Blueprints por perfis de acesso e templates baseados em `base.html`:

* **Autenticação (`/auth/login`, `/auth/liberar` SSO)**: 
  * Formulários clássicos com verificação ativa da Session do SQLAlchemy. 
  * O endpoint especial `/validate-ticket` recebe o `ticket` via hand-shake POST que o Hub Principal disparou, validando e unificando a autoridade de Login JWT da base do Hub, atestando e dando vida ao painel local de quem estiver acessando a página.

* **Operação Usuário (`/usuario` - Blueprints)**:
  * CRUD - Criação limpa, Visualização, e Exportações personalizadas de Fonogramas que pertencem somente aquele usuário autenticado. Em massa ou um a um.
  * **O Cérebro da Inserção (Upload Module - O coração do workflow da equipe):** Uma página limpa JS com UI responsiva/DragAndDrop com `script.js` e o motor `upload_service`. O script em vanilla lê e valida Planilhas bagunçadas (CSV/XLSX) direto na UI do cliente sem commitar ainda no Database. Processa os acertos visando dar Feedback Visual amigável via `fetch` dos "Conflitos do Fonograma Musical". Então o cliente clica "Salvar apenas validados" e empurra de verdade para a engine do sistema.

* **Administrador Core (`/admin` - Blueprints)**:
  * Dashboard de KPIs e Insights Gerais (Quantidade Global de Entidades, Pendentes, Taxa de Aprovações/Recusas, Analytics de Produtos Ativos do Selo etc).
  * Controle global das Obras + Configuração dos Enumerators e do CRUD dos Operadores base.
  * Gerenciamento de Upload Retornos (`upload_retorno`): A rotina onde os layouts XML/EXP/CSV herméticos que o ECAD fisicamente devolveu processamento são importados. Os "Sinais Verde e Vermelho" são disparados num lote em massa e os items PENDENTES do catálogo finalmente são dados baixa ("ACEITO" / "RECUSADO" + Cód. de erro da Receita/Governo/Assoc).

## 4. O Módulo Processador e Validador (`/shared`)
Contém o cérebro das regras de negócio pesada do mercado de Direitos Autorais e os parsers dos motores conversores.

* `validador.py`: Regras estritas lógicas para homologação musical: O ISRC (regex e módulo validador alfanumérico estrito `BRXXXYYNNNNN`), Mod11 de CNPJ/CPF via métodos matemáticos, formatação coerente de Duração. Dicionários de códigos autorizados em blocos (`GENEROS`: Sertanejo, Indie, etc. e `CATEGORIA_INTERPRETE`: Violão, Bateria). E as métricas críticas do modelo, como: A soma percentual `Interpretes(%) + Musicos(%) + Produtor(%) == 100%`.
* `processador.py`: O "Puxador de Dados" robusto de Arquivos Customizados. Tenta heurísticamente auto-detectar o _encoding_ (usando magic bits com `chardet`) e delimitadores vírgula/ponto, com fallback inteligente. Converte e mapeia cabeçalhos em Inglês ou mal formatados dos clientes para dados legíveis pelo ORM (ex: header 'composer  ' > passa pra > 'autores' com conversão Regex/Regex-Pipe de Subfunções).
* `gerador_ecad.py`: O serializador nativo e fundamental do App. Traduz Banco de Dados para a língua do ECAD. Quando a Administração fecha/conclui os items e "Gera Lote":
  * Executa construtores procedurais longos como `_build_obm1`, `_build_obm2`, `_build_fon1`, injetando cada autor da árvore.
  * Produz buffers e strings exatas de **Largura Posicional Fixa** (`_zpad` de padding zeroes, `_pad` para truncações limitantes dos bytes ASCII e sanitarização Unicode em `NFKD`).
  * Embuti os identificadores exigidos pelo sistema vetorial antigo do ECAD (`'0661OBM1'`, tipos P/J, flags de `'S/N'`, código numérico de idioma `'PTN'`). Confecciona o arquivo final com extenção `.txt`. Este script também suporta planilhas nativas em `openpyxl` customizadas com as cores da paleta UX (estilo: Cor de "identificação" com fontes dark e light dinâmicas).

## 5. A API Restful Total Base (`/api` - Blueprint)
Distribuídas em files como `fonogramas_api.py`, `ecad_api.py` e `validacao_api.py`.
Fornece acessos integrados JSON Stateless autônomos listados na spec UI do `Flasgger` (Acesso do Dev via: `/api/docs/`):
* Todas isentas do Anti-Robot local `@csrf.exempt`. Contudo protegida modularmente pelo interceptor de Auth Token `@require_api_auth`.
* Fornecimento pleno de Operação/Criação, Paginação, Update ou Delete das Obras a partir do zero ou de dicionários vindos inteiros por POST com tratamento Rollback e de Exception do SQLAlchemy. Este é o caminho perfeito para integrações externas da Intranet da empresa (Sistemas em Node, Desktop Java, etc).

## 6. O Fluxo Real Simplificado do Operador (Step-by-Step)
1. O Representante/Consultor Musical loga pelo formulário ou via Redirecionamento Remoto.
2. Vai em Importar Múltiplo Fonogramas e solta um super Planilhão (csv ou xslx), exportado anteriormente dos seus sistemas paralelos, na Área Upload.
3. O JS dispara um AJAX multipart. O servidor Flask usa a biblioteca `chardet/csv.Sniffer/pandas` para fatiar, limpar lixos de string do Unicode e checar integridade matemática no validador de música.
4. O servidor devolve no mesmo layout do Operador um Feedback UI (Ex: "⚠️ Célula C14 com Erro - Autor está marcando CPF Inválido" ou "Soma conexa do Fono X está 90% ao invés de 100%").
5. O Representante lê, volta, conserta o que estiver em erro.
6. Uma vez com os dados confirmados sem impedimentos, clica _"Salvar"_, o backend comita no SQLAlchemy a leva e carimba a versão deles com status `PENDENTE`. 
7. Meses e Dias depois, um Usuário de Cargo **Administrador** (Diretor de Cadastro, por ex), clica em Menu ECAD e seleciona os blocos validados (ISRCs prontos). Então roda a Ação: **GERAR ENVIO**.
8. O Flask trava o lote inteiro, atualiza todo mundo para `ENVIADO` para não haver duplo-upload. Abre o script do gerador texto longo legível pela Máquina da Matriz. O Admin resgata e envia por e-mail ou portal à entidade legal controladora.
9. Num momento futuro o ECAD devolve a devolutiva homologada ou recusada. O Admin sobe a devolução no módulo _"Retornos ECAD"_. O Módulo faz o Parsing visual, traça o Protocolo de Relacionamento criado anteriormente, e sela para todo o sempre no banco de dados com `ACEITO`! (Finalizando o clímax da API).

## Conclusão da Análise Sistêmica
É um sistema robusto, de alta coesão e baixo acoplamento nos escopos do Domínio, excelente isolamento da Camada Service, possuindo um ambiente flexível e rico para a gestão crítica dos ISRC e complexos pagamentos do escopo musical. Totalmente moderno para o paradigma Flask + jQueryVanilla, estável, e documentado de forma clara para escalabilidade.
