package com.sbacem.fonogramas;

import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import java.util.Map;
import java.util.HashMap;

/**
 * Cliente Spring para API de Fonogramas ECAD/ABRAMUS
 * 
 * Usa RestTemplate do Spring Framework
 * 
 * Dependências Maven:
 * <dependency>
 *     <groupId>org.springframework</groupId>
 *     <artifactId>spring-web</artifactId>
 *     <version>6.0.0</version>
 * </dependency>
 */
public class ClienteFonogramasAPI_Spring {
    
    private final String baseUrl;
    private final RestTemplate restTemplate;
    
    public ClienteFonogramasAPI_Spring(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.restTemplate = new RestTemplate();
    }
    
    /**
     * Lista fonogramas com paginação e filtros
     */
    public Map<String, Object> listarFonogramas(int page, int perPage, String search, String situacao) {
        String url = baseUrl + "/api/v1/fonogramas?page={page}&per_page={perPage}";
        
        Map<String, Object> params = new HashMap<>();
        params.put("page", page);
        params.put("perPage", perPage);
        
        if (search != null && !search.isEmpty()) {
            url += "&search={search}";
            params.put("search", search);
        }
        if (situacao != null && !situacao.isEmpty()) {
            url += "&situacao={situacao}";
            params.put("situacao", situacao);
        }
        
        ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class, params);
        return response.getBody();
    }
    
    /**
     * Obtém um fonograma por ID
     */
    public Map<String, Object> obterFonograma(int id) {
        String url = baseUrl + "/api/v1/fonogramas/{id}";
        ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class, id);
        return response.getBody();
    }
    
    /**
     * Obtém um fonograma por ISRC
     */
    public Map<String, Object> obterFonogramaPorISRC(String isrc) {
        String url = baseUrl + "/api/v1/fonogramas/isrc/{isrc}";
        ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class, isrc);
        return response.getBody();
    }
    
    /**
     * Cria um novo fonograma
     */
    public Map<String, Object> criarFonograma(Map<String, Object> dadosFonograma) {
        String url = baseUrl + "/api/v1/fonogramas";
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(dadosFonograma, headers);
        ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);
        
        return response.getBody();
    }
    
    /**
     * Atualiza um fonograma existente
     */
    public Map<String, Object> atualizarFonograma(int id, Map<String, Object> dadosFonograma) {
        String url = baseUrl + "/api/v1/fonogramas/{id}";
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(dadosFonograma, headers);
        ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.PUT, request, Map.class, id);
        
        return response.getBody();
    }
    
    /**
     * Deleta um fonograma
     */
    public Map<String, Object> deletarFonograma(int id) {
        String url = baseUrl + "/api/v1/fonogramas/{id}";
        ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.DELETE, null, Map.class, id);
        return response.getBody();
    }
    
    /**
     * Obtém estatísticas do sistema
     */
    public Map<String, Object> obterEstatisticas() {
        String url = baseUrl + "/api/v1/stats";
        ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
        return response.getBody();
    }
    
    /**
     * Exemplo de uso
     */
    public static void main(String[] args) {
        ClienteFonogramasAPI_Spring cliente = new ClienteFonogramasAPI_Spring("http://localhost:5001");
        
        try {
            // Listar fonogramas
            Map<String, Object> lista = cliente.listarFonogramas(1, 20, null, null);
            System.out.println("Resposta: " + lista);
            
            // Criar fonograma
            Map<String, Object> novoFonograma = new HashMap<>();
            novoFonograma.put("isrc", "BRUM71601234");
            novoFonograma.put("titulo", "Música Teste");
            novoFonograma.put("duracao", "03:45");
            novoFonograma.put("ano_lanc", 2024);
            novoFonograma.put("genero", "Pop");
            novoFonograma.put("titulo_obra", "Obra Teste");
            novoFonograma.put("prod_nome", "Produtora Teste");
            novoFonograma.put("prod_doc", "11222333000181");
            novoFonograma.put("prod_perc", 25.0);
            
            Map<String, Object> resultado = cliente.criarFonograma(novoFonograma);
            System.out.println("Fonograma criado: " + resultado);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}



