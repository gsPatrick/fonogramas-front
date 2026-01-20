"""
Teste de Estresse - Sistema de Fonogramas SBACEM
Testa a capacidade do sistema com grande volume de dados
"""

import time
import random
import string
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# Configuração
BASE_URL = "http://localhost:5001"
NUM_FONOGRAMAS = 1000  # Número de fonogramas para gerar
CONCURRENT_REQUESTS = 10  # Requisições simultâneas

# Dados de exemplo para geração aleatória
GENEROS = ["Pop", "Rock", "MPB", "Sertanejo", "Forró", "Axé", "Funk", "Samba", "Pagode", "Gospel"]
VERSOES = ["original", "remix", "ao vivo", "acústico"]
IDIOMAS = ["PT", "EN", "ES", "FR"]
ASSOCIACOES = ["ABRAMUS", "UBC", "SBACEM", "AMAR", "SICAM"]


def gerar_isrc():
    """Gera um ISRC aleatório válido"""
    pais = "BR"
    registrante = "UM7"
    ano = str(random.randint(20, 26))
    codigo = ''.join(random.choices(string.digits, k=5))
    return f"{pais}{registrante}{ano}{codigo}"


def gerar_cpf():
    """Gera um CPF aleatório (apenas formato, não validado)"""
    return ''.join(random.choices(string.digits, k=11))


def gerar_cnpj():
    """Gera um CNPJ aleatório (apenas formato, não validado)"""
    return ''.join(random.choices(string.digits, k=14))


def gerar_fonograma():
    """Gera dados de um fonograma aleatório"""
    return {
        "isrc": gerar_isrc(),
        "titulo": f"Música Teste {random.randint(1, 99999)}",
        "versao": random.choice(VERSOES),
        "duracao": f"{random.randint(2, 5)}:{random.randint(10, 59):02d}",
        "ano_grav": random.randint(2020, 2026),
        "ano_lanc": random.randint(2020, 2026),
        "idioma": random.choice(IDIOMAS),
        "genero": random.choice(GENEROS),
        "titulo_obra": f"Obra Musical {random.randint(1, 99999)}",
        "autores": f"Autor Teste|{gerar_cpf()}|COMPOSITOR|100",
        "interpretes": f"Intérprete Teste|{gerar_cpf()}|PRINCIPAL|100|{random.choice(ASSOCIACOES)}",
        "prod_nome": f"Produtora Teste {random.randint(1, 999)}",
        "prod_doc": gerar_cnpj(),
        "prod_perc": 100,
        "prod_assoc": random.choice(ASSOCIACOES)
    }


def teste_insercao_massa():
    """Testa inserção em massa de fonogramas no banco"""
    print("\n" + "=" * 60)
    print("TESTE 1: Inserção em Massa no Banco de Dados")
    print("=" * 60)
    
    import sys
    sys.path.insert(0, '.')
    
    from app import app, db
    from models import Fonograma
    from shared.fonograma_service import criar_fonograma_do_dataframe
    
    with app.app_context():
        # Conta registros antes
        antes = Fonograma.query.count()
        print(f"Fonogramas antes: {antes}")
        
        tempos = []
        erros = 0
        
        print(f"\nInserindo {NUM_FONOGRAMAS} fonogramas...")
        
        inicio_total = time.time()
        
        for i in range(NUM_FONOGRAMAS):
            dados = gerar_fonograma()
            inicio = time.time()
            
            try:
                fonograma = criar_fonograma_do_dataframe(dados)
                db.session.add(fonograma)
                
                # Commit a cada 100 registros para performance
                if (i + 1) % 100 == 0:
                    db.session.commit()
                    print(f"  {i + 1}/{NUM_FONOGRAMAS} inseridos...")
                
                tempos.append(time.time() - inicio)
            except Exception as e:
                db.session.rollback()
                erros += 1
        
        # Commit final
        db.session.commit()
        
        tempo_total = time.time() - inicio_total
        depois = Fonograma.query.count()
        
        print(f"\n📊 RESULTADOS:")
        print(f"  • Fonogramas inseridos: {depois - antes}")
        print(f"  • Erros: {erros}")
        print(f"  • Tempo total: {tempo_total:.2f}s")
        print(f"  • Taxa: {(depois - antes) / tempo_total:.1f} inserções/segundo")
        print(f"  • Tempo médio por inserção: {statistics.mean(tempos) * 1000:.2f}ms")
        print(f"  • Tempo máximo: {max(tempos) * 1000:.2f}ms")
        
        return depois - antes


def teste_consulta_performance():
    """Testa performance de consultas"""
    print("\n" + "=" * 60)
    print("TESTE 2: Performance de Consultas")
    print("=" * 60)
    
    import sys
    sys.path.insert(0, '.')
    
    from app import app, db
    from models import Fonograma
    from sqlalchemy import or_
    
    with app.app_context():
        total = Fonograma.query.count()
        print(f"Total de fonogramas no banco: {total}")
        
        testes = []
        
        # Teste 1: Query simples com limit
        inicio = time.time()
        result = Fonograma.query.limit(100).all()
        tempo = time.time() - inicio
        testes.append(("Query simples (LIMIT 100)", tempo, len(result)))
        
        # Teste 2: Query com filtros
        inicio = time.time()
        result = Fonograma.query.filter_by(genero="Pop").limit(100).all()
        tempo = time.time() - inicio
        testes.append(("Query filtro gênero", tempo, len(result)))
        
        # Teste 3: Query com LIKE
        inicio = time.time()
        result = Fonograma.query.filter(Fonograma.titulo.ilike('%Teste%')).limit(100).all()
        tempo = time.time() - inicio
        testes.append(("Query LIKE título", tempo, len(result)))
        
        # Teste 4: Query com múltiplos filtros
        inicio = time.time()
        result = Fonograma.query.filter(
            or_(
                Fonograma.isrc.ilike('%BR%'),
                Fonograma.titulo.ilike('%Música%')
            )
        ).order_by(Fonograma.created_at.desc()).limit(100).all()
        tempo = time.time() - inicio
        testes.append(("Query complexa (OR + ORDER)", tempo, len(result)))
        
        # Teste 5: Contagem total
        inicio = time.time()
        count = Fonograma.query.count()
        tempo = time.time() - inicio
        testes.append(("COUNT total", tempo, count))
        
        # Teste 6: Agregação por gênero
        inicio = time.time()
        from sqlalchemy import func
        result = db.session.query(
            Fonograma.genero, 
            func.count(Fonograma.id)
        ).group_by(Fonograma.genero).all()
        tempo = time.time() - inicio
        testes.append(("GROUP BY gênero", tempo, len(result)))
        
        print(f"\n📊 RESULTADOS:")
        for nome, tempo, qtd in testes:
            status = "✅" if tempo < 0.1 else "⚠️" if tempo < 0.5 else "❌"
            print(f"  {status} {nome}: {tempo * 1000:.2f}ms (retornou {qtd})")


def teste_api_carga():
    """Testa a API com múltiplas requisições simultâneas"""
    print("\n" + "=" * 60)
    print("TESTE 3: Carga na API")
    print("=" * 60)
    
    def fazer_requisicao(url):
        inicio = time.time()
        try:
            response = requests.get(url, timeout=30)
            return time.time() - inicio, response.status_code
        except Exception as e:
            return time.time() - inicio, 0
    
    # Login primeiro
    session = requests.Session()
    login_response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@sbacem.org.br", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Falha no login da API")
        return
    
    endpoints = [
        "/api/fonogramas?page=1&per_page=50",
        "/api/fonogramas?page=1&per_page=100",
        "/api/estatisticas",
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\nTestando: {endpoint}")
        
        tempos = []
        erros = 0
        
        with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
            futures = [executor.submit(fazer_requisicao, url) for _ in range(50)]
            
            for future in as_completed(futures):
                tempo, status = future.result()
                tempos.append(tempo)
                if status != 200:
                    erros += 1
        
        print(f"  • Requisições: 50")
        print(f"  • Concorrência: {CONCURRENT_REQUESTS}")
        print(f"  • Erros: {erros}")
        print(f"  • Tempo médio: {statistics.mean(tempos) * 1000:.2f}ms")
        print(f"  • Tempo máximo: {max(tempos) * 1000:.2f}ms")
        print(f"  • Tempo mínimo: {min(tempos) * 1000:.2f}ms")


def limpar_dados_teste():
    """Remove os dados de teste do banco"""
    print("\n" + "=" * 60)
    print("LIMPEZA: Removendo dados de teste")
    print("=" * 60)
    
    import sys
    sys.path.insert(0, '.')
    
    from app import app, db
    from models import Fonograma
    
    with app.app_context():
        antes = Fonograma.query.count()
        
        # Remove fonogramas de teste (que têm "Música Teste" no título)
        deletados = Fonograma.query.filter(
            Fonograma.titulo.like('%Música Teste%')
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        depois = Fonograma.query.count()
        
        print(f"  • Fonogramas antes: {antes}")
        print(f"  • Deletados: {deletados}")
        print(f"  • Fonogramas depois: {depois}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔥 TESTE DE ESTRESSE - SISTEMA DE FONOGRAMAS SBACEM")
    print("=" * 60)
    print(f"Configuração:")
    print(f"  • Fonogramas a gerar: {NUM_FONOGRAMAS}")
    print(f"  • Requisições concorrentes: {CONCURRENT_REQUESTS}")
    
    try:
        # Teste 1: Inserção em massa
        inseridos = teste_insercao_massa()
        
        # Teste 2: Performance de consultas
        teste_consulta_performance()
        
        # Teste 3: Carga na API
        teste_api_carga()
        
        # Perguntar se quer limpar
        print("\n" + "=" * 60)
        resposta = input("Deseja remover os dados de teste? (s/n): ")
        if resposta.lower() == 's':
            limpar_dados_teste()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ TESTE DE ESTRESSE FINALIZADO")
    print("=" * 60)
