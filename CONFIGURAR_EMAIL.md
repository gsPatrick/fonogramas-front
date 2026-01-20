# 📧 Como Configurar a Recuperação de Senha por Email

Este guia explica como configurar o envio de emails para a funcionalidade de recuperação de senha do sistema SBACEM.

---

## 📋 Visão Geral

O sistema permite que usuários redefinam suas senhas através de um link enviado por email. Para isso funcionar em **produção**, você precisa configurar um servidor SMTP.

---

## ⚙️ Configuração

### Opção 1: Gmail (Recomendado para testes)

Para usar o Gmail como servidor de email:

1. **Crie uma Senha de App no Google:**
   - Acesse https://myaccount.google.com/security
   - Ative a verificação em duas etapas (se não estiver ativa)
   - Vá em "Senhas de app" ou acesse: https://myaccount.google.com/apppasswords
   - Crie uma nova senha de app para "Outro (nome personalizado)"
   - Copie a senha de 16 caracteres gerada

2. **Configure as variáveis de ambiente:**

   **Windows (PowerShell):**
   ```powershell
   $env:MAIL_SERVER = "smtp.gmail.com"
   $env:MAIL_PORT = "587"
   $env:MAIL_USE_TLS = "true"
   $env:MAIL_USERNAME = "seu-email@gmail.com"
   $env:MAIL_PASSWORD = "xxxx-xxxx-xxxx-xxxx"  # Senha de app (16 chars)
   $env:MAIL_DEFAULT_SENDER = "seu-email@gmail.com"
   ```

   **Windows (CMD):**
   ```cmd
   set MAIL_SERVER=smtp.gmail.com
   set MAIL_PORT=587
   set MAIL_USE_TLS=true
   set MAIL_USERNAME=seu-email@gmail.com
   set MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
   set MAIL_DEFAULT_SENDER=seu-email@gmail.com
   ```

   **Linux/Mac:**
   ```bash
   export MAIL_SERVER=smtp.gmail.com
   export MAIL_PORT=587
   export MAIL_USE_TLS=true
   export MAIL_USERNAME=seu-email@gmail.com
   export MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
   export MAIL_DEFAULT_SENDER=seu-email@gmail.com
   ```

3. **Inicie o servidor após configurar as variáveis:**
   ```bash
   python app.py
   ```

---

### Opção 2: Servidor SMTP Corporativo

Se sua empresa possui um servidor de email próprio:

```powershell
$env:MAIL_SERVER = "smtp.suaempresa.com.br"
$env:MAIL_PORT = "587"
$env:MAIL_USE_TLS = "true"
$env:MAIL_USERNAME = "sistema@suaempresa.com.br"
$env:MAIL_PASSWORD = "senha-do-email"
$env:MAIL_DEFAULT_SENDER = "noreply@suaempresa.com.br"
```

> ⚠️ Consulte seu departamento de TI para obter as configurações corretas do servidor SMTP.

---

### Opção 3: Serviços de Email Transacional

Para envio em grande escala, considere serviços especializados:

| Serviço | Configuração SMTP |
|---------|-------------------|
| **SendGrid** | `smtp.sendgrid.net`, porta 587 |
| **Mailgun** | `smtp.mailgun.org`, porta 587 |
| **Amazon SES** | `email-smtp.us-east-1.amazonaws.com`, porta 587 |

---

## 🔧 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `MAIL_SERVER` | Endereço do servidor SMTP | `smtp.gmail.com` |
| `MAIL_PORT` | Porta do servidor | `587` |
| `MAIL_USE_TLS` | Usar TLS (recomendado) | `true` |
| `MAIL_USERNAME` | Email ou usuário SMTP | `user@empresa.com` |
| `MAIL_PASSWORD` | Senha ou senha de app | `senha123` |
| `MAIL_DEFAULT_SENDER` | Email remetente | `noreply@empresa.com` |

---

## ✅ Testar a Configuração

1. Inicie o servidor com as variáveis configuradas
2. Acesse http://localhost:5001/auth/forgot-password
3. Digite um email cadastrado no sistema
4. Verifique se o email foi recebido

**No console do servidor você verá:**
```
[EMAIL] Enviado com sucesso para usuario@email.com
```

---

## ⚠️ Modo Desenvolvimento (Sem Email)

Se as variáveis `MAIL_USERNAME` e `MAIL_PASSWORD` não estiverem configuradas, o sistema entra em **modo desenvolvimento**:

- O link de recuperação é impresso apenas no **console do servidor**
- Nenhum email é enviado
- Útil para testes locais

```
========================================================
📧 EMAIL DE RECUPERAÇÃO DE SENHA (MODO DEV)
========================================================
Para: usuario@email.com
Assunto: SBACEM - Recuperação de Senha
--------------------------------------------------------
Link de recuperação:
>>> http://localhost:5001/auth/reset-password/abc123... <<<
========================================================
```

---

## 🔒 Segurança

1. **Nunca** compartilhe as credenciais de email
2. Use **senhas de app** ao invés da senha principal (Gmail)
3. Considere usar um email dedicado para o sistema
4. O link de recuperação expira em **1 hora**
5. O sistema **não revela** se um email está cadastrado ou não

---

## 📞 Suporte

Se tiver problemas com o envio de emails:

1. Verifique se as variáveis estão configuradas corretamente
2. Teste a conexão SMTP com uma ferramenta externa
3. Verifique firewalls que possam bloquear porta 587
4. Consulte os logs em `logs/app.log`
