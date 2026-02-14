package com.sbacem.fonogramas;

import java.net.CookieManager;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Cliente Java para API de Fonogramas ECAD/SBACEM
 * 
 * Requer Java 11+ e Jackson para JSON
 * 
 * Dependências Maven:
 * <dependency>
 *     <groupId>com.fasterxml.jackson.core</groupId>
 *     <artifactId>jackson-databind</artifactId>
 *     <version>2.15.2</version>
 * </dependency>
 */
public class ClienteFonogramasAPI {
    
    private final String baseUrl;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    public ClienteFonogramasAPI(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        
        // Configura HttpClient com CookieManager para manter a sessão (Login)
        this.httpClient = HttpClient.newBuilder()
            .cookieHandler(new CookieManager())
            .connectTimeout(Duration.ofSeconds(10))
            .build();
            
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * Realiza login no sistema
     */
    public ApiResponse login(String email, String password) {
        try {
            Map<String, String> credenciais = new HashMap<>();
            credenciais.put("email", email);
            credenciais.put("password", password);
            
            String json = objectMapper.writeValueAsString(credenciais);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/auth/login"))
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .header("Content-Type", "application/json")
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return objectMapper.readValue(response.body(), ApiResponse.class);
            
        } catch (Exception e) {
            throw new RuntimeException("Erro ao realizar login", e);
        }
    }

    /**
     * Realiza logout do sistema
     */
    public ApiResponse logout() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/auth/logout"))
                .POST(HttpRequest.BodyPublishers.noBody())
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return objectMapper.readValue(response.body(), ApiResponse.class);
            
        } catch (Exception e) {
            throw new RuntimeException("Erro ao realizar logout", e);
        }
    }
    
    /**
     * Lista fonogramas com paginação e filtros
     */
    public ApiResponse listarFonogramas(int page, int perPage, String search, String situacao) {
        try {
            StringBuilder url = new StringBuilder(baseUrl + "/api/fonogramas");
            url.append("?page=").append(page);
            url.append("&per_page=").append(perPage);
            
            if (search != null && !search.isEmpty()) {
                url.append("&busca=").append(java.net.URLEncoder.encode(search, "UTF-8"));
            }
            if (situacao != null && !situacao.isEmpty()) {
                url.append("&status=").append(situacao);
            }
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url.toString()))
                .GET()
                .header("Content-Type", "application/json")
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            return objectMapper.readValue(response.body(), ApiResponse.class);
        } catch (Exception e) {
            throw new RuntimeException("Erro ao listar fonogramas", e);
        }
    }
    
    /**
     * Obtém um fonograma por ID
     */
    public ApiResponse obterFonograma(int id) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/fonogramas/" + id))
                .GET()
                .header("Content-Type", "application/json")
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            return objectMapper.readValue(response.body(), ApiResponse.class);
        } catch (Exception e) {
            throw new RuntimeException("Erro ao obter fonograma", e);
        }
    }
    
    /**
     * Obtém um fonograma por ISRC
     */
    public ApiResponse obterFonogramaPorISRC(String isrc) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/fonogramas/isrc/" + isrc))
                .GET()
                .header("Content-Type", "application/json")
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            return objectMapper.readValue(response.body(), ApiResponse.class);
        } catch (Exception e) {
            throw new RuntimeException("Erro ao obter fonograma por ISRC", e);
        }
    }
    
    /**
     * Cria um novo fonograma
     */
    public ApiResponse criarFonograma(Map<String, Object> dadosFonograma) {
        try {
            String json = objectMapper.writeValueAsString(dadosFonograma);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/fonogramas"))
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .header("Content-Type", "application/json")
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            return objectMapper.readValue(response.body(), ApiResponse.class);
        } catch (Exception e) {
            throw new RuntimeException("Erro ao criar fonograma", e);
        }
    }
    
    /**
     * Atualiza um fonograma existente
     */
    public ApiResponse atualizarFonograma(int id, Map<String, Object> dadosFonograma) {
        try {
            String json = objectMapper.writeValueAsString(dadosFonograma);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/fonogramas/" + id))
                .PUT(HttpRequest.BodyPublishers.ofString(json))
                .header("Content-Type", "application/json")
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            return objectMapper.readValue(response.body(), ApiResponse.class);
        } catch (Exception e) {
            throw new RuntimeException("Erro ao atualizar fonograma", e);
        }
    }
    
    /**
     * Deleta um fonograma
     */
    public ApiResponse deletarFonograma(int id) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/fonogramas/" + id))
                .DELETE()
                .header("Content-Type", "application/json")
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            return objectMapper.readValue(response.body(), ApiResponse.class);
        } catch (Exception e) {
            throw new RuntimeException("Erro ao deletar fonograma", e);
        }
    }
    
    /**
     * Obtém estatísticas do sistema
     */
    public ApiResponse obterEstatisticas() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/fonogramas/stats"))
                .GET()
                .header("Content-Type", "application/json")
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            return objectMapper.readValue(response.body(), ApiResponse.class);
        } catch (Exception e) {
            throw new RuntimeException("Erro ao obter estatísticas", e);
        }
    }
    
    /**
     * Verifica se a API está funcionando
     */
    public ApiResponse healthCheck() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/health"))
                .GET()
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            return objectMapper.readValue(response.body(), ApiResponse.class);
        } catch (Exception e) {
            throw new RuntimeException("Erro no health check", e);
        }
    }
    
    /**
     * Classe para representar a resposta da API
     */
    public static class ApiResponse {
        private boolean success;
        private Object data;
        private String message;
        private Object error; // Pode ser String ou Objeto
        private Map<String, Object> meta;
        
        // Getters e Setters
        public boolean isSuccess() { return success; }
        public void setSuccess(boolean success) { this.success = success; }
        
        public Object getData() { return data; }
        public void setData(Object data) { this.data = data; }
        
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
        
        public Object getError() { return error; }
        public void setError(Object error) { this.error = error; }
        
        public Map<String, Object> getMeta() { return meta; }
        public void setMeta(Map<String, Object> meta) { this.meta = meta; }
    }
}



