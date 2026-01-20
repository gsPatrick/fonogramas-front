# 🔌 Como Integrar na Intranet - Java

Guia completo para integrar a API REST do Sistema de Fonogramas SBACEM em aplicações Java.

---

## 📋 Índice

1. [Configuração da API](#-configuração-da-api)
2. [Autenticação](#-autenticação)
3. [Endpoints Disponíveis](#-endpoints-disponíveis)
4. [Exemplos Java](#-exemplos-java)
5. [Tratamento de Erros](#-tratamento-de-erros)
6. [Configuração CORS](#-configuração-cors)

---

## 🌐 Configuração da API

### URL Base

| Ambiente | URL |
|----------|-----|
| Desenvolvimento | `http://localhost:5001/api` |
| Produção | `http://servidor.empresa.com:5001/api` |
| Documentação | `http://localhost:5001/api/docs` |

### Health Check

Antes de integrar, verifique se a API está funcionando:

```bash
curl http://localhost:5001/health
```

Resposta esperada:
```json
{
    "status": "healthy",
    "database": "ok",
    "version": "1.0.0"
}
```

---

## 🔐 Autenticação

A API usa autenticação por sessão (cookies). Você precisa fazer login primeiro.

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
    "email": "usuario@empresa.com",
    "password": "senha123"
}
```

**Resposta de sucesso:**
```json
{
    "success": true,
    "message": "Login realizado com sucesso",
    "user": {
        "id": 1,
        "email": "usuario@empresa.com",
        "nome": "Usuário",
        "is_admin": false
    }
}
```

### Logout

```http
POST /api/auth/logout
```

---

## 📡 Endpoints Disponíveis

### Sistema

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/api/docs` | Documentação Swagger |

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Dados do usuário logado |

### Fonogramas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/fonogramas` | Listar fonogramas |
| GET | `/api/fonogramas/{id}` | Obter fonograma por ID |
| GET | `/api/fonogramas/isrc/{isrc}` | Obter fonograma por ISRC |
| POST | `/api/fonogramas` | Criar fonograma |
| PUT | `/api/fonogramas/{id}` | Atualizar fonograma |
| DELETE | `/api/fonogramas/{id}` | Deletar fonograma |

### Parâmetros de Listagem

```http
GET /api/fonogramas?page=1&per_page=20&busca=termo&status_ecad=ACEITO&genero=Pop
```

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | int | Página (padrão: 1) |
| `per_page` | int | Itens por página (padrão: 20, máx: 100) |
| `busca` | string | Busca em ISRC, título, produtor |
| `status_ecad` | string | NAO_ENVIADO, ENVIADO, ACEITO, RECUSADO |
| `genero` | string | Gênero musical |

### Validação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/validar/isrc` | Validar ISRC |
| POST | `/api/validar/cpf` | Validar CPF |
| POST | `/api/validar/cnpj` | Validar CNPJ |

### Estatísticas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/estatisticas` | Estatísticas gerais |

---

## 💻 Exemplos Java

### Cliente Completo (Java 11+)

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.CookieManager;
import java.time.Duration;

public class FonogramasClient {
    
    private static final String API_URL = "http://localhost:5001";
    private final HttpClient client;
    
    public FonogramasClient() {
        // Cliente com suporte a cookies (sessão)
        this.client = HttpClient.newBuilder()
            .cookieHandler(new CookieManager())
            .connectTimeout(Duration.ofSeconds(10))
            .build();
    }
    
    /**
     * Faz login na API
     */
    public boolean login(String email, String senha) throws Exception {
        String json = String.format(
            "{\"email\":\"%s\",\"password\":\"%s\"}", 
            email, senha
        );
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL + "/api/auth/login"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(json))
            .build();
        
        HttpResponse<String> response = client.send(
            request, 
            HttpResponse.BodyHandlers.ofString()
        );
        
        return response.statusCode() == 200;
    }
    
    /**
     * Lista fonogramas com paginação
     */
    public String listarFonogramas(int page, int perPage) throws Exception {
        String url = String.format(
            "%s/api/fonogramas?page=%d&per_page=%d",
            API_URL, page, perPage
        );
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(
            request,
            HttpResponse.BodyHandlers.ofString()
        );
        
        return response.body();
    }
    
    /**
     * Busca fonograma por ISRC
     */
    public String buscarPorISRC(String isrc) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL + "/api/fonogramas/isrc/" + isrc))
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(
            request,
            HttpResponse.BodyHandlers.ofString()
        );
        
        if (response.statusCode() == 200) {
            return response.body();
        }
        return null;
    }
    
    /**
     * Cria um novo fonograma
     */
    public String criarFonograma(String fonogramaJson) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL + "/api/fonogramas"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(fonogramaJson))
            .build();
        
        HttpResponse<String> response = client.send(
            request,
            HttpResponse.BodyHandlers.ofString()
        );
        
        return response.body();
    }
    
    /**
     * Verifica se a API está saudável
     */
    public boolean healthCheck() throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL + "/health"))
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(
            request,
            HttpResponse.BodyHandlers.ofString()
        );
        
        return response.statusCode() == 200;
    }
    
    // Exemplo de uso
    public static void main(String[] args) {
        FonogramasClient cliente = new FonogramasClient();
        
        try {
            // Verificar saúde da API
            if (!cliente.healthCheck()) {
                System.out.println("API não está disponível!");
                return;
            }
            System.out.println("✅ API funcionando");
            
            // Login (substituir por credenciais reais)
            if (cliente.login("seu-usuario@empresa.com", "sua-senha")) {
                System.out.println("✅ Login realizado");
                
                // Listar fonogramas
                String fonogramas = cliente.listarFonogramas(1, 10);
                System.out.println("Fonogramas: " + fonogramas);
                
            } else {
                System.out.println("❌ Falha no login");
            }
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

### Spring Boot Service

```java
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.Map;

@Service
public class FonogramaApiService {
    
    @Value("${fonogramas.api.url:http://localhost:5001}")
    private String apiUrl;
    
    private final RestTemplate restTemplate;
    private String sessionCookie;
    
    public FonogramaApiService() {
        this.restTemplate = new RestTemplate();
    }
    
    /**
     * Faz login e armazena o cookie de sessão
     */
    public boolean login(String email, String senha) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            Map<String, String> body = Map.of(
                "email", email,
                "password", senha
            );
            
            HttpEntity<Map<String, String>> request = 
                new HttpEntity<>(body, headers);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(
                apiUrl + "/api/auth/login",
                request,
                Map.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                // Armazena o cookie de sessão
                this.sessionCookie = response.getHeaders()
                    .getFirst(HttpHeaders.SET_COOKIE);
                return true;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return false;
    }
    
    /**
     * Lista fonogramas
     */
    public Map<String, Object> listarFonogramas(int page, int perPage) {
        HttpHeaders headers = new HttpHeaders();
        if (sessionCookie != null) {
            headers.add(HttpHeaders.COOKIE, sessionCookie);
        }
        
        HttpEntity<?> request = new HttpEntity<>(headers);
        
        String url = String.format(
            "%s/api/fonogramas?page=%d&per_page=%d",
            apiUrl, page, perPage
        );
        
        ResponseEntity<Map> response = restTemplate.exchange(
            url,
            HttpMethod.GET,
            request,
            Map.class
        );
        
        return response.getBody();
    }
    
    /**
     * Obtém um fonograma por ID
     */
    public Map<String, Object> obterFonograma(int id) {
        HttpHeaders headers = new HttpHeaders();
        if (sessionCookie != null) {
            headers.add(HttpHeaders.COOKIE, sessionCookie);
        }
        
        HttpEntity<?> request = new HttpEntity<>(headers);
        
        ResponseEntity<Map> response = restTemplate.exchange(
            apiUrl + "/api/fonogramas/" + id,
            HttpMethod.GET,
            request,
            Map.class
        );
        
        return response.getBody();
    }
}
```

---

## 📝 Formato JSON

### Criar/Atualizar Fonograma

```json
{
    "isrc": "BRUM71601234",
    "titulo": "Música Exemplo",
    "versao": "original",
    "duracao": "03:45",
    "ano_grav": 2023,
    "ano_lanc": 2024,
    "idioma": "PT",
    "genero": "Pop",
    "titulo_obra": "Obra Musical 1",
    "prod_nome": "Produtora XYZ",
    "prod_doc": "11222333000181",
    "prod_perc": 25.0,
    "prod_assoc": "ABRAMUS",
    "autores": [
        {
            "nome": "João Silva",
            "cpf": "11144477735",
            "funcao": "COMPOSITOR",
            "percentual": 50.0
        },
        {
            "nome": "Maria Santos",
            "cpf": "22255588846",
            "funcao": "LETRISTA",
            "percentual": 50.0
        }
    ],
    "interpretes": [
        {
            "nome": "Carlos Oliveira",
            "doc": "33366699957",
            "categoria": "PRINCIPAL",
            "percentual": 75.0,
            "associacao": "ABRAMUS"
        }
    ]
}
```

---

## ❌ Tratamento de Erros

### Formato de Erro

```json
{
    "success": false,
    "error": "Mensagem de erro",
    "code": "ERROR_CODE"
}
```

### Códigos HTTP

| Código | Significado | Ação |
|--------|-------------|------|
| 200 | Sucesso | ✅ |
| 201 | Criado | ✅ |
| 400 | Erro de validação | Verificar dados enviados |
| 401 | Não autenticado | Fazer login |
| 403 | Sem permissão | Verificar perfil do usuário |
| 404 | Não encontrado | Verificar ID/ISRC |
| 429 | Rate limit | Aguardar 1 minuto |
| 500 | Erro interno | Contactar suporte |

### Exemplo de Tratamento

```java
try {
    String resultado = cliente.criarFonograma(json);
    // Processar sucesso
} catch (HttpClientErrorException e) {
    if (e.getStatusCode() == HttpStatus.BAD_REQUEST) {
        System.out.println("Dados inválidos: " + e.getResponseBodyAsString());
    } else if (e.getStatusCode() == HttpStatus.UNAUTHORIZED) {
        System.out.println("Sessão expirada. Refaça login.");
        cliente.login(email, senha);
    }
}
```

---

## 🔒 Configuração CORS

A API já está configurada para aceitar requisições de qualquer origem. Para restringir em produção, edite `app.py`:

```python
cors_config = {
    r"/api/*": {
        "origins": [
            "http://intranet.empresa.com",
            "https://app.empresa.com"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
}
```

---

## 📦 Dependências Maven

```xml
<!-- Se usar Spring Boot -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- Se usar Apache HttpClient -->
<dependency>
    <groupId>org.apache.httpcomponents.client5</groupId>
    <artifactId>httpclient5</artifactId>
    <version>5.2</version>
</dependency>

<!-- Para parsing JSON -->
<dependency>
    <groupId>com.google.code.gson</groupId>
    <artifactId>gson</artifactId>
    <version>2.10</version>
</dependency>
```

---

## 🧪 Testando a Integração

### Teste com cURL

```bash
# 1. Health Check
curl http://localhost:5001/health

# 2. Login (salva cookie) - substituir por credenciais reais
curl -c cookies.txt -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"seu-usuario@empresa.com","password":"sua-senha"}'

# 3. Listar fonogramas (usa cookie)
curl -b cookies.txt http://localhost:5001/api/fonogramas

# 4. Criar fonograma
curl -b cookies.txt -X POST http://localhost:5001/api/fonogramas \
  -H "Content-Type: application/json" \
  -d '{"isrc":"BRUM71699999","titulo":"Teste API","duracao":"03:00","ano_lanc":2024,"genero":"Rock","titulo_obra":"Obra Teste","prod_nome":"Produtora","prod_doc":"11222333000181","prod_perc":100}'
```

---

## 💡 Dicas

| Dica | Descrição |
|------|-----------|
| 🔐 Sessão | Sempre mantenha os cookies entre requisições |
| ⏱️ Timeout | Configure timeout de 10-30 segundos |
| 🔄 Retry | Implemente retry para erros 5xx |
| 📝 Logs | Registre todas as requisições para debug |
| ✅ Validação | Valide dados antes de enviar |
| 🧪 Testes | Teste com cURL antes de implementar em Java |

---

## 📞 Suporte

Para dúvidas sobre a integração:
1. Consulte a documentação Swagger em `/api/docs`
2. Verifique os logs em `logs/app.log`
3. Teste os endpoints com cURL primeiro

---

**Versão da API:** 1.0.0  
**Última atualização:** Janeiro 2026
