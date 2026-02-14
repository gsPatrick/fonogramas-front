package com.sbacem.fonogramas;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Script de teste para validação da API e Cliente Java
 */
public class TestarAPI {

    public static void main(String[] args) {
        System.out.println("=== INICIANDO TESTE DE INTEGRAÇÃO API ===");

        // 1. Inicializar Cliente
        ClienteFonogramasAPI cliente = new ClienteFonogramasAPI("http://localhost:5001");

        try {
            // 2. Health Check
            System.out.println("\n[1] Verificando status da API...");
            var health = cliente.healthCheck();
            if (health.isSuccess()) {
                System.out.println("✅ API Online: " + health.getMessage());
            } else {
                System.out.println("❌ Erro na API: " + health.getError());
                return;
            }

            // 3. Login (Ajuste as credenciais conforme seu ambiente)
            System.out.println("\n[2] Realizando Login...");
            // IMPORTANTE: Substitua por um usuário admin válido do seu banco de dados
            var login = cliente.login("admin@sbacem.org.br", "admin123");
            if (login.isSuccess()) {
                System.out.println("✅ Login realizado com sucesso!");
            } else {
                System.out.println("❌ Falha no login: " + login.getMessage());
                return;
            }

            // 4. Criar Fonograma com Participantes
            System.out.println("\n[3] Criando Fonograma com Listas...");
            Map<String, Object> novoFonograma = new HashMap<>();
            String isrcTeste = "BRTEST26" + System.currentTimeMillis() % 100000; // ISRC único

            novoFonograma.put("isrc", isrcTeste);
            novoFonograma.put("titulo", "Música Teste Java API " + System.currentTimeMillis());
            novoFonograma.put("titulo_obra", "Obra Teste");
            novoFonograma.put("duracao", "03:30");
            novoFonograma.put("ano_lanc", 2026);
            novoFonograma.put("genero", "Rock");
            novoFonograma.put("prod_nome", "Produtora Java");
            novoFonograma.put("prod_perc", 100.0);

            // Lista de Autores
            List<Map<String, Object>> autores = new ArrayList<>();
            Map<String, Object> autor1 = new HashMap<>();
            autor1.put("nome", "João Java");
            autor1.put("cpf", "111.222.333-44");
            autor1.put("funcao", "AUTOR");
            autor1.put("percentual", 50.0);
            autores.add(autor1);

            Map<String, Object> autor2 = new HashMap<>();
            autor2.put("nome", "Maria Code");
            autor2.put("cpf", "555.666.777-88");
            autor2.put("funcao", "COMPOSITOR");
            autor2.put("percentual", 50.0);
            autores.add(autor2);

            novoFonograma.put("autores", autores);

            // Lista de Intérpretes
            List<Map<String, Object>> interpretes = new ArrayList<>();
            Map<String, Object> interp1 = new HashMap<>();
            interp1.put("nome", "Banda Java");
            interp1.put("categoria", "INTERPRETE");
            interp1.put("percentual", 100.0);
            interpretes.add(interp1);

            novoFonograma.put("interpretes", interpretes);

            var criacao = cliente.criarFonograma(novoFonograma);
            if (criacao.isSuccess()) {
                System.out.println("✅ Fonograma criado: " + criacao.getData());
            } else {
                System.out.println("❌ Erro ao criar: " + criacao.getError());
                if (criacao.getError() instanceof Map) {
                    System.out.println("Detalhes: " + criacao.getError());
                }
            }

            // 5. Listar e validar
            System.out.println("\n[4] Listando último fonograma criado...");
            var busca = cliente.obterFonogramaPorISRC(isrcTeste);
            if (busca.isSuccess()) {
                Map<String, Object> dados = (Map<String, Object>) busca.getData();
                System.out.println("✅ Dados recuperados:");
                System.out.println("   Título: " + dados.get("titulo"));
                System.out.println("   Autores: " + dados.get("autores"));
                // Validação simples
                List<?> autoresRecup = (List<?>) dados.get("autores");
                if (autoresRecup != null && autoresRecup.size() == 2) {
                    System.out.println("   ✅ Validação de Autores: OK (2 encontrados)");
                } else {
                    System.out.println("   ❌ Validação de Autores: FALHO ("
                            + (autoresRecup != null ? autoresRecup.size() : 0) + " encontrados)");
                }
            } else {
                System.out.println("❌ Erro ao buscar: " + busca.getError());
            }

            System.out.println("\n=== TESTE FINALIZADO ===");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
