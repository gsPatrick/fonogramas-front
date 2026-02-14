
import sqlite3
import os

# Caminho para o banco de dados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'fonogramas.db')

def migrate():
    print(f"Migrando banco de dados em: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("Banco de dados não encontrado!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Novos campos para a tabela 'autores'
    autores_columns = [
        ('cae_ipi', 'VARCHAR(20)'),
        ('data_nascimento', 'VARCHAR(10)'),
        ('nacionalidade', 'VARCHAR(50)'),
    ]
    
    # Novos campos para a tabela 'interpretes'
    interpretes_columns = [
        ('cae_ipi', 'VARCHAR(20)'),
        ('data_nascimento', 'VARCHAR(10)'),
        ('nacionalidade', 'VARCHAR(50)'),
    ]
    
    # Novos campos para a tabela 'editoras'
    editoras_columns = [
        ('nacionalidade', 'VARCHAR(50)'),
    ]
    
    # Novos campos para a tabela 'fonogramas'
    fonogramas_columns = [
        ('subdivisao_estrangeiro', 'VARCHAR(50)'),
        ('publicacao_simultanea', 'BOOLEAN DEFAULT 0'),
    ]
    
    migrations = [
        ('autores', autores_columns),
        ('interpretes', interpretes_columns),
        ('editoras', editoras_columns),
        ('fonogramas', fonogramas_columns),
    ]
    
    for table, columns in migrations:
        print(f"\n--- Tabela: {table} ---")
        for col_name, col_type in columns:
            try:
                print(f"  Adicionando coluna {col_name}...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                print(f"  Sucesso: {col_name} adicionada.")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"  Info: Coluna {col_name} já existe.")
                else:
                    print(f"  Erro ao adicionar {col_name}: {e}")
                
    conn.commit()
    conn.close()
    print("\nMigração concluída com sucesso!")

if __name__ == "__main__":
    migrate()
