# 🎵 Fluxo do Sistema de Gestão de Fonogramas

Este documento descreve o ciclo de vida completo de um fonograma dentro do sistema, desde a sua importação até o processamento do retorno do ECAD.

## 1. Importação e Cadastro
O primeiro passo é colocar os fonogramas no sistema. Isso pode ser feito de duas formas:
- **Individualmente:** Pelo formulário "Novo Fonograma".
- **Em Lote (Massiva):** Via arquivo Excel/CSV.

✅ **Diferencial do Sistema:** Ao importar, o sistema já aplica **regras de validação** (ex: CPF válido, soma de percentuais = 100%, ISRC único). Isso evita que dados incorretos cheguem ao ECAD.

## 2. Validação e Conferência
Após importados, os fonogramas ficam com status `PENDENTE` ou `NAO_ENVIADO`.
O gestor pode revisar os dados no painel, verificar se falta alguma informação (ex: ISRC ou Documento do Produtor) e corrigir antes do envio.

## 3. Geração do Arquivo de Envio (ECAD)
Esta é a etapa onde o sistema "fala" com a associação.
1. O usuário acessa o menu **Envios ECAD > Novo Envio**.
2. Seleciona os fonogramas que deseja enviar.
3. O sistema gera um arquivo (Excel ou padrão SISRC) pronto para ser enviado à associação (Abramus, UBC, Socinpro, etc).
4. O status dos fonogramas muda automaticamente para `ENVIADO`.

## 4. Processamento do Retorno (O "End Point")
Após a associação processar o arquivo, ela devolve um arquivo de retorno confirmando o cadastro ou apontando erros.

**Como testar no sistema:**
1. Vá em **Retornos ECAD > Upload**.
2. Selecione o envio correspondente.
3. Faça o upload do arquivo de retorno (ex: `retorno_ecad_teste.csv`).

### O que o sistema faz automaticamente:
*   **Se ACEITO:** Atualiza o status do fonograma para `ACEITO` (verde) e salva o Código ECAD gerado.
*   **Se RECUSADO:** Atualiza para `RECUSADO` (vermelho), exibe o motivo do erro (ex: "CPF do produtor inválido") e guarda o histórico.

---

## 🧪 Arquivos para Teste de Demonstração

No repositório, incluímos arquivos prontos para realizar essa demonstração para o cliente:

| Arquivo | Descrição |
| :--- | :--- |
| `fonograma_realista_teste.csv` | Arquivo para importar 2 fonogramas de exemplo. |
| `retorno_ecad_teste.csv` | Arquivo que simula a resposta do ECAD (1 Aceito, 1 Recusado). |

### Roteiro de Demo Sugerido:
1. **Importar Lote:** Subir o `fonograma_realista_teste.csv`. Mostrar que entraram 2 fonogramas.
2. **Gerar Envio:** Criar um envio com esses 2 fonogramas. Mostrar o status mudando para `ENVIADO`.
3. **Processar Retorno:** Subir o `retorno_ecad_teste.csv`.
    *   Mostrar que o *Garota de Ipanema* ficou **Verde (Aceito)**.
    *   Mostrar que o *Mas Que Nada* ficou **Vermelho (Recusado)** e ler o erro na tela.
