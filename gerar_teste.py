import pandas as pd
import os

# Dados fictícios para teste de importação
data = [
    {
        "isrc": "BRABC2400003",
        "titulo": "Teste XLS Antigo 01",
        "duracao": "03:30",
        "ano_lanc": 2024,
        "ano_grav": 2024,
        "genero": "Pop",
        "titulo_obra": "Obra XLS 01",
        "prod_nome": "Produtor Legacy",
        "prod_doc": "11144477735",
        "prod_perc": "100",
        "autores": "Autor Legacy|11144477735|COMPOSITOR|100",
        "interpretes": "Interprete Legacy|11144477735|PRINCIPAL|100",
        "situacao": "ATIVO",
        "versao": "Original",
        "idioma": "PT"
    }
]

# Criar DataFrame
df = pd.DataFrame(data)

# Caminho do arquivo
output_file_xlsx = 'teste_importacao_admin.xlsx'
output_file_xls = 'teste_importacao_admin_antigo.xls'

# Salvar como XLSX (Padrão)
try:
    df.to_excel(output_file_xlsx, index=False)
    print(f"Sucesso XLSX: {os.path.abspath(output_file_xlsx)}")
except Exception as e:
    print(f"Erro XLSX: {e}")

# Salvar como XLS (Antigo) - Requer xlwt
try:
    import xlwt
    df.to_excel(output_file_xls, index=False, engine='xlwt')
    print(f"Sucesso XLS: {os.path.abspath(output_file_xls)}")
except ImportError:
    print("Biblioteca 'xlwt' nao instalada. Pulando geracao do .xls")
except Exception as e:
    print(f"Erro XLS: {e}")
