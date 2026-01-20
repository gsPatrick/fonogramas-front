# 🎵 Sistema de Fonogramas SBACEM

Sistema web completo para gerenciamento de fonogramas musicais, com integração ECAD, validação de dados e geração de relatórios Excel.

![Status](https://img.shields.io/badge/Status-Produção-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-lightgrey)

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Início Rápido](#-início-rápido)
- [Documentação](#-documentação)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Requisitos do Sistema](#-requisitos-do-sistema)
- [Configuração de Produção](#-configuração-de-produção)

---

## ✨ Funcionalidades

### 👤 Painel do Usuário
- ✅ Dashboard com estatísticas (Total, Enviados, Aceitos, Recusados)
- ✅ Listagem de fonogramas com filtros combinados
- ✅ Busca por ISRC, título, produtor
- ✅ Edição individual e em lote
- ✅ Upload de CSV/Excel
- ✅ Download de templates CSV e Excel
- ✅ Exportação formatada para Excel

### 🛠️ Painel Administrativo
- ✅ Gerenciamento de envios ECAD
- ✅ Processamento de retornos ECAD
- ✅ Operações em lote (importar, atualizar, excluir, editar)
- ✅ Auditoria de alterações
- ✅ Gerenciamento de usuários
- ✅ Relatórios por gênero, produtor, período

### 🔒 Segurança
- ✅ Autenticação com login/senha
- ✅ Recuperação de senha por email
- ✅ Proteção CSRF
- ✅ Rate limiting (100 req/min)
- ✅ Headers de segurança (XSS, CSP, etc)
- ✅ Sessões seguras

### 🔌 API REST
- ✅ CRUD completo de fonogramas
- ✅ Autenticação por sessão
- ✅ Documentação Swagger em `/api/docs`
- ✅ Health check em `/health`

---

## 🚀 Início Rápido

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o servidor
```bash
python app.py
```

### 3. Acessar no navegador
```
http://localhost:5001
```

### 4. Primeiro Acesso
```
Consulte o arquivo CREDENCIAIS_ADMIN.txt (entregue separadamente)
ou peça ao administrador do sistema.
```

> ⚠️ **IMPORTANTE:** Altere a senha padrão imediatamente após o primeiro acesso!

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [Como Rodar o Código](como%20rodar%20o%20codigo.md) | Guia completo de instalação e execução |
| [Integração Java](como%20integrar%20na%20intranet%20java.md) | Como integrar a API na intranet Java |
| [API Docs](http://localhost:5001/api/docs) | Documentação interativa Swagger |

---

## 📁 Estrutura do Projeto

```
FONOGRAMA/
├── 📄 app.py                  # Aplicação principal Flask
├── 📄 models.py               # Modelos de banco de dados
├── 📄 config.py               # Configurações
├── 📄 requirements.txt        # Dependências Python
│
├── 📂 auth/                   # Módulo de autenticação
│   ├── routes.py              # Rotas (login, logout, recuperar senha)
│   └── services/              # Serviços (email)
│
├── 📂 usuario/                # Painel do usuário
│   ├── routes.py              # Rotas do usuário
│   ├── services/              # Serviços (fonograma, upload, export)
│   └── templates/             # Templates HTML
│
├── 📂 admin/                  # Painel administrativo
│   ├── routes.py              # Rotas do admin
│   ├── services/              # Serviços (envio, retorno, lote)
│   └── templates/             # Templates HTML
│
├── 📂 api/                    # API REST
│   ├── __init__.py            # Blueprint da API
│   ├── fonogramas_api.py      # CRUD de fonogramas
│   ├── auth_api.py            # Autenticação API
│   └── validacao_api.py       # Validações (ISRC, CPF, CNPJ)
│
├── 📂 shared/                 # Módulos compartilhados
│   ├── processador.py         # Processamento de CSV
│   ├── validador.py           # Validações
│   ├── gerador_excel.py       # Geração de Excel
│   └── fonograma_service.py   # Operações CRUD
│
├── 📂 templates/              # Templates globais
├── 📂 static/                 # CSS, JS, imagens
├── 📂 instance/               # Banco de dados SQLite
├── 📂 logs/                   # Logs da aplicação
├── 📂 uploads/                # Arquivos temporários
└── 📂 outputs/                # Arquivos gerados
```

---

## 💻 Requisitos do Sistema

### Mínimos
- Python 3.8+
- 512MB RAM
- 100MB espaço em disco

### Recomendados
- Python 3.11+
- 2GB RAM
- SSD para melhor performance

### Dependências Python
```
Flask>=3.0.0
Flask-WTF>=1.2.0
Flask-Login>=0.6.0
Flask-SQLAlchemy>=3.1.0
flask-cors>=4.0.0
flasgger>=0.9.7
pandas>=2.2.0
openpyxl>=3.1.0
chardet>=5.0.0
requests>=2.31.0
```

---

## ⚙️ Configuração de Produção

### Variáveis de Ambiente

```bash
# Obrigatório em produção
export FLASK_ENV=production
export SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria

# Opcional (para email)
export MAIL_SERVER=smtp.seuservidor.com
export MAIL_PORT=587
export MAIL_USERNAME=seu@email.com
export MAIL_PASSWORD=suasenha

# Opcional (banco externo)
export DATABASE_URL=postgresql://user:pass@host/database
```

### Executar com Waitress (Windows)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5001 app:app
```

### Executar com Gunicorn (Linux)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

---

## 🏥 Monitoramento

### Health Check
```bash
curl http://localhost:5001/health
```

Resposta:
```json
{
    "status": "healthy",
    "database": "ok",
    "version": "1.0.0",
    "timestamp": "2026-01-09T12:00:00"
}
```

### Logs
Os logs são salvos em `logs/app.log`:
```bash
tail -f logs/app.log
```

---

## 🧪 Testes

### Teste de Estresse
```bash
python scripts/stress_test.py
```

Resultados típicos:
- **1.800+ inserções/segundo**
- **Consultas < 5ms**
- **Suporte a 10.000+ fonogramas**

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação acima
2. Verifique os logs em `logs/app.log`
3. Teste o endpoint `/health`

---

**Versão:** 1.0.0  
**Última atualização:** Janeiro 2026
