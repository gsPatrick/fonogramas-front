
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
    
    columns_to_add = [
        ('pais_origem', 'VARCHAR(100)'),
        ('paises_adicionais', 'TEXT'),
        ('flag_nacional', 'VARCHAR(20)'),
        ('classificacao_trilha', 'VARCHAR(50)'),
        ('tipo_arranjo', 'VARCHAR(20)')
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            print(f"Adicionando coluna {col_name}...")
            cursor.execute(f"ALTER TABLE fonogramas ADD COLUMN {col_name} {col_type}")
            print(f"Sucesso: {col_name} adicionada.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"Info: Coluna {col_name} já existe.")
            else:
                print(f"Erro ao adicionar {col_name}: {e}")
                
    conn.commit()
    conn.close()
    print("Migração concluída.")

if __name__ == "__main__":
    migrate()
