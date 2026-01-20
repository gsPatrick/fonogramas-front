# 🚀 Como Rodar o Código

Guia completo para instalar e executar o Sistema de Fonogramas SBACEM.

---

## 📋 Pré-requisitos

| Requisito | Versão Mínima | Como Verificar |
|-----------|---------------|----------------|
| Python | 3.8+ | `python --version` |
| pip | 20.0+ | `pip --version` |

### Não tem Python?

Baixe em: https://www.python.org/downloads/

> ⚠️ **Windows:** Marque a opção "Add Python to PATH" durante a instalação!

---

## 📥 Instalação Passo a Passo

### 1. Abrir o Terminal

| Sistema | Como Abrir |
|---------|------------|
| Windows | `Win + X` → PowerShell ou Terminal |
| Mac | `Cmd + Espaço` → digite "Terminal" |
| Linux | `Ctrl + Alt + T` |

### 2. Navegar até a pasta do projeto

```bash
cd C:\Users\Leandro\Desktop\FONOGRAMA
```

> 💡 Ajuste o caminho conforme a localização do seu projeto.

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

Isso instalará automaticamente:
- Flask (servidor web)
- Flask-WTF (proteção CSRF)
- Flask-Login (autenticação)
- Flask-SQLAlchemy (banco de dados)
- pandas (processamento de dados)
- openpyxl (geração de Excel)
- E outras dependências...

⏳ Aguarde alguns minutos para a instalação completar.

### 4. Executar o servidor

```bash
python app.py
```

Você verá algo como:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5001
Press CTRL+C to quit
```

### 5. Acessar no navegador

Abra seu navegador e acesse:

```
http://localhost:5001
```

---

## 🔐 Primeiro Acesso

Na primeira execução, o sistema cria um usuário administrador padrão.

> ⚠️ **IMPORTANTE:** Consulte o administrador do sistema para obter as credenciais de acesso. Em produção, altere a senha padrão imediatamente!

---

## ✅ Verificar se Está Funcionando

1. **Página de login** deve aparecer
2. **Faça login** com as credenciais acima
3. **Dashboard** deve mostrar estatísticas
4. **Menu lateral** com opções funcionando

### Verificar via Terminal

```bash
curl http://localhost:5001/health
```

Resposta esperada:
```json
{"status": "healthy", "database": "ok"}
```

---

## ⏹️ Parar o Servidor

No terminal, pressione:

```
Ctrl + C
```

---

## ❌ Problemas Comuns

### "python não é reconhecido"

**Solução 1:** Use `python3` ao invés de `python`:
```bash
python3 app.py
```

**Solução 2:** Reinstale o Python marcando "Add to PATH"

---

### "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

Se não funcionar:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### "Port already in use" / "Porta em uso"

A porta 5001 já está sendo usada. Opções:

1. **Fechar outro programa** que usa a porta
2. **Mudar a porta** no arquivo `app.py` (última linha):

```python
app.run(debug=True, port=5002)  # Mude 5001 para 5002
```

---

### Erro de permissão (Windows)

Execute o PowerShell como **Administrador**:
- Clique direito no PowerShell → "Executar como administrador"

---

### Erro ao instalar dependências

```bash
pip3 install -r requirements.txt
```

Ou atualize o pip:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configurações Opcionais

### Alterar a Porta

Edite `app.py` na última linha:
```python
app.run(debug=True, port=5002)
```

### Acessar de Outro Computador na Rede

```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

Acesse via IP da máquina: `http://192.168.1.X:5001`

---

## 🏭 Executar em Produção

### Windows (Waitress)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5001 app:app
```

### Linux/Mac (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Variáveis de Ambiente

```bash
# Windows PowerShell
$env:FLASK_ENV = "production"
$env:SECRET_KEY = "sua-chave-secreta-muito-longa-e-aleatoria"
$env:CORS_ORIGINS = "http://intranet.empresa.com,https://app.empresa.com"

# Configuração de Email (ver CONFIGURAR_EMAIL.md)
$env:MAIL_SERVER = "smtp.empresa.com"
$env:MAIL_PORT = "587"
$env:MAIL_USERNAME = "sistema@empresa.com"
$env:MAIL_PASSWORD = "senha-do-email"

# Linux/Mac
export FLASK_ENV=production
export SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria
export CORS_ORIGINS=http://intranet.empresa.com
```

---

## 📁 O que Acontece na Primeira Execução?

1. **Pasta `instance/`** é criada com o banco de dados
2. **Pasta `uploads/`** é criada para arquivos temporários
3. **Pasta `outputs/`** é criada para arquivos gerados
4. **Pasta `logs/`** é criada para logs da aplicação
5. **Usuário admin** é criado automaticamente (se não existir)

---

## 💡 Dicas

| Dica | Descrição |
|------|-----------|
| 🖥️ Terminal aberto | Mantenha o terminal aberto enquanto o servidor estiver rodando |
| 🔄 Auto-reload | Em modo debug, mudanças no código recarregam automaticamente |
| 📝 Logs | Consulte `logs/app.log` para debugar problemas |
| 🏥 Health check | Acesse `/health` para verificar status do sistema |

---

## 📞 Próximos Passos

1. ✅ Servidor rodando
2. 📝 Faça login como admin
3. 👤 Crie novos usuários (Admin → Configurações → Usuários)
4. 📊 Importe fonogramas via CSV ou manualmente
5. 📤 Gerencie envios para o ECAD

---

**Precisa de ajuda?** Consulte o [README.md](README.md) para mais informações.
