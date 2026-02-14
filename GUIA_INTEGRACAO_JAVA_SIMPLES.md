# 🔌 Guia Simples: Como Integrar com o Sistema Java (Atualizado)

Este guia explica como fazer seu sistema Java se comunicar com a API do Sistema de Fonogramas SBACEM, incluindo autenticação e envio de listas de participantes.

---

## 📋 Pré-requisitos

O cliente Java atualizado utiliza a biblioteca **Jackson** para processar JSON.
Adicione ao seu `pom.xml` (Maven):

```xml
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.15.2</version>
</dependency>
```

---

## 🚀 Passo 1: Iniciar o Servidor SBACEM

Certifique-se de que o servidor Python está rodando:
```bash
python app.py
```
(Ou use `INICIAR_SERVIDOR.bat` no Windows)

---

## 🔐 Passo 2: Usar o Cliente Java

O arquivo `exemplos_java/ClienteFonogramasAPI.java` já contém toda a lógica necessária.
Veja como usar no seu código:

### 1. Inicialização e Login (Obrigatório)

O sistema agora exige login para todas as operações. O cliente gerencia os cookies de sessão automaticamente.

```java
import com.sbacem.fonogramas.ClienteFonogramasAPI;

public class Main {
    public static void main(String[] args) {
        // Conectar
        ClienteFonogramasAPI cliente = new ClienteFonogramasAPI("http://localhost:5001");
        
        // Fazer Login
        var login = cliente.login("admin@sbacem.org.br", "admin123");
        
        if (login.isSuccess()) {
            System.out.println("Login OK!");
        } else {
            System.out.println("Erro: " + login.getMessage());
            return;
        }
        
        // Agora você pode chamar outros métodos...
    }
}
```

---

## ➕ Passo 3: Criar Fonograma com Participantes

Agora você pode (e deve) enviar as listas de Autores, Intérpretes e Músicos diretamente no JSON.

```java
Map<String, Object> novoFonograma = new HashMap<>();
novoFonograma.put("isrc", "BRUM72600001");
novoFonograma.put("titulo", "Minha Música Nova");
// ... outros campos básicos

// Adicionar Autores
List<Map<String, Object>> autores = new ArrayList<>();
Map<String, Object> autor = new HashMap<>();
autor.put("nome", "João Silva");
autor.put("cpf", "111.222.333-44");
autor.put("funcao", "AUTOR"); // AUTOR, COMPOSITOR, VERSIONISTA
autor.put("percentual", 100.0);
autores.add(autor);

novoFonograma.put("autores", autores);

// Adicionar Intérpretes
List<Map<String, Object>> interpretes = new ArrayList<>();
Map<String, Object> interprete = new HashMap<>();
interprete.put("nome", "Banda Legal");
interprete.put("categoria", "INTERPRETE");
interprete.put("percentual", 100.0);
interpretes.add(interprete);

novoFonograma.put("interpretes", interpretes);

// Enviar
var resposta = cliente.criarFonograma(novoFonograma);
```

### Alternativa: Requisição Simples (Form Data)

Se você **não quiser usar JSON/Jackson**, pode enviar os dados como formulário (`application/x-www-form-urlencoded`).
A API agora aceita ambos os formatos.

Exemplo sem biblioteca JSON:
```java
String dados = "isrc=BRUM72600002&titulo=Musica Sem Json&prod_perc=100";

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:5001/api/fonogramas"))
    .header("Content-Type", "application/x-www-form-urlencoded")
    .POST(HttpRequest.BodyPublishers.ofString(dados))
    .build();
```
*Nota: Para listas complexas (autores/intérpretes), recomendamos usar JSON, pois o formato de formulário para listas pode ser verboso (`autores[0][nome]=...`).*

---

## 📡 Endpoints Disponíveis

| Método | Função Java | Descrição |
|--------|-------------|-----------|
| `login` | `cliente.login(email, senha)` | Autentica e inicia sessão |
| `logout` | `cliente.logout()` | Encerra sessão |
| `listarFonogramas` | `cliente.listarFonogramas(...)` | Lista com filtros |
| `obterFonograma` | `cliente.obterFonograma(id)` | Busca por ID |
| `obterFonogramaPorISRC` | `cliente.obterFonogramaPorISRC(isrc)` | Busca por ISRC |
| `criarFonograma` | `cliente.criarFonograma(dados)` | Cria novo registro |
| `atualizarFonograma` | `cliente.atualizarFonograma(id, dados)` | Atualiza existente |
| `deletarFonograma` | `cliente.deletarFonograma(id)` | Remove registro |

---

## 🧪 Teste Automatizado

Foi criado um arquivo `exemplos_java/TestarAPI.java` que demonstra o fluxo completo:
1. Conecta
2. Faz Login
3. Cria Fonograma completo
4. Verifica os dados

Você pode usar este arquivo como base para seus testes de integração.

---

## 📋 O que você precisa saber

O sistema SBACEM funciona como um **serviço web separado**. Seu sistema Java vai se comunicar com ele através de **requisições HTTP** (como quando você acessa um site).

```
┌──────────────────┐                    ┌──────────────────┐
│  Seu Sistema     │  ── requisição ──► │  SBACEM          │
│  Java            │  ◄── resposta ───  │  (porta 5001)    │
└──────────────────┘                    └──────────────────┘
```

**Não precisa instalar nada no Java** - você só faz chamadas HTTP para o servidor SBACEM.

---

## 🚀 Passo 1: Iniciar o Servidor SBACEM

Antes de qualquer coisa, o servidor SBACEM precisa estar rodando.

### No Windows:

1. Abra o **PowerShell** ou **Prompt de Comando**
2. Navegue até a pasta do SBACEM:
   ```
   cd C:\Caminho\Para\FONOGRAMA
   ```
3. Instale as dependências (só na primeira vez):
   ```
   pip install -r requirements.txt
   ```
4. Inicie o servidor:
   ```
   python app.py
   ```

Você verá:
```
* Running on http://127.0.0.1:5001
```

✅ **Pronto!** O servidor está rodando.

---

## 🔐 Passo 2: Fazer Login (Autenticação)

Antes de usar qualquer função, você precisa fazer login.

### Requisição:
```
POST http://localhost:5001/api/auth/login
Content-Type: application/json

{
    "email": "seu-usuario@empresa.com",
    "password": "sua-senha"
}
```

### Resposta de sucesso:
```json
{
    "success": true,
    "message": "Login realizado com sucesso"
}
```

### Exemplo em Java:

```java
import java.net.http.*;
import java.net.URI;
import java.net.CookieManager;

// 1. Criar cliente HTTP que guarda cookies (importante!)
HttpClient cliente = HttpClient.newBuilder()
    .cookieHandler(new CookieManager())  // ← guarda a sessão
    .build();

// 2. Fazer login
String loginJson = "{\"email\":\"usuario@empresa.com\",\"password\":\"senha123\"}";

HttpRequest loginRequest = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:5001/api/auth/login"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(loginJson))
    .build();

HttpResponse<String> response = cliente.send(loginRequest, 
    HttpResponse.BodyHandlers.ofString());

System.out.println(response.body());  // Mostra a resposta
```

⚠️ **IMPORTANTE:** Use o mesmo objeto `cliente` para todas as requisições, senão você perde a sessão!

---

## 📋 Passo 3: Listar Fonogramas

Depois de logado, você pode listar os fonogramas.

### Requisição:
```
GET http://localhost:5001/api/fonogramas
```

### Exemplo em Java:

```java
// Usando o MESMO cliente do login
HttpRequest listRequest = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:5001/api/fonogramas"))
    .GET()
    .build();

HttpResponse<String> response = cliente.send(listRequest, 
    HttpResponse.BodyHandlers.ofString());

System.out.println(response.body());  // Lista de fonogramas em JSON
```

### Resposta:
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "isrc": "BRUM71601234",
            "titulo": "Nome da Música",
            "genero": "Pop"
        }
    ]
}
```

---

## 🔍 Passo 4: Buscar por ISRC

Buscar um fonograma específico pelo código ISRC.

### Requisição:
```
GET http://localhost:5001/api/fonogramas/isrc/BRUM71601234
```

### Exemplo em Java:

```java
String isrc = "BRUM71601234";

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:5001/api/fonogramas/isrc/" + isrc))
    .GET()
    .build();

HttpResponse<String> response = cliente.send(request, 
    HttpResponse.BodyHandlers.ofString());

System.out.println(response.body());
```

---

## ➕ Passo 5: Criar um Fonograma

Enviar dados de um novo fonograma.

### Requisição:
```
POST http://localhost:5001/api/fonogramas
Content-Type: application/json

{
    "isrc": "BRUM71699999",
    "titulo": "Minha Música",
    "titulo_obra": "Minha Obra",
    "duracao": "03:45",
    "genero": "Pop",
    "prod_nome": "Produtora XYZ",
    "prod_doc": "12345678000199",
    "prod_perc": 100
}
```

### Exemplo em Java:

```java
String fonogramaJson = """
    {
        "isrc": "BRUM71699999",
        "titulo": "Minha Música",
        "titulo_obra": "Minha Obra",
        "duracao": "03:45",
        "genero": "Pop",
        "prod_nome": "Produtora XYZ",
        "prod_doc": "12345678000199",
        "prod_perc": 100
    }
    """;

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:5001/api/fonogramas"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(fonogramaJson))
    .build();

HttpResponse<String> response = cliente.send(request, 
    HttpResponse.BodyHandlers.ofString());

System.out.println(response.body());
```

---

## 📡 Resumo dos Endpoints

| Ação | Método | URL |
|------|--------|-----|
| Login | POST | `/api/auth/login` |
| Logout | POST | `/api/auth/logout` |
| Listar fonogramas | GET | `/api/fonogramas` |
| Buscar por ID | GET | `/api/fonogramas/{id}` |
| Buscar por ISRC | GET | `/api/fonogramas/isrc/{isrc}` |
| Criar | POST | `/api/fonogramas` |
| Atualizar | PUT | `/api/fonogramas/{id}` |
| Deletar | DELETE | `/api/fonogramas/{id}` |
| Health Check | GET | `/health` |

---

## ❌ Erros Comuns

### "Connection refused"
O servidor SBACEM não está rodando. Execute `python app.py`.

### "401 Não autenticado"
Você não fez login ou a sessão expirou. Faça login novamente.

### "403 Acesso negado"
Você não tem permissão para essa ação.

### "404 Não encontrado"
O fonograma com esse ID/ISRC não existe.

---

## 💡 Dicas Importantes

1. **Sempre use o MESMO objeto HttpClient** para todas as requisições
2. **O servidor precisa estar rodando** antes de fazer requisições
3. **Em produção**, troque `localhost` pelo IP do servidor
4. **Mantenha a sessão** - não crie um novo cliente para cada requisição

---

## 🧪 Testar Rapidamente

Para testar se está funcionando, abra o navegador e acesse:

```
http://localhost:5001/health
```

Se mostrar `{"status": "healthy"}`, o servidor está OK!

---

## 📞 Precisa de Mais Ajuda?

Consulte a documentação completa em:
- `como integrar na intranet java.md` (exemplos avançados)
- `README.md` (visão geral do sistema)
- `/api/docs` no navegador (documentação interativa)
