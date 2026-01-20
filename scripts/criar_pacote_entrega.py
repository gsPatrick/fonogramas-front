# Script para criar banco limpo e ZIP de entrega
import os
import shutil
from datetime import datetime

# Diretório do projeto
PROJECT_DIR = r'c:\Users\Leandro\Desktop\FONOGRAMA'
OUTPUT_DIR = PROJECT_DIR

# Nome do ZIP
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
zip_name = f'FONOGRAMA_ENTREGA_{timestamp}'

# Criar banco de dados limpo (apenas com admin)
print("=" * 50)
print("Criando banco de dados limpo...")
print("=" * 50)

# Criar diretório temporário para o pacote
temp_dir = os.path.join(OUTPUT_DIR, '_temp_entrega')
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Copiar arquivos do projeto (excluindo coisas desnecessárias)
exclude_patterns = [
    '__pycache__',
    '.git',
    '*.pyc',
    'instance',  # Não copiar banco existente
    'uploads',
    'outputs',
    'logs',
    '_temp_entrega',
    'backup_',  # Backups antigos
    '*.zip',
    'Conversas externas',
    '.gemini',
]

def should_exclude(path, name):
    full_path = os.path.join(path, name)
    for pattern in exclude_patterns:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return True
        elif pattern in full_path or name == pattern:
            return True
    return False

# Copiar arquivos
for item in os.listdir(PROJECT_DIR):
    if should_exclude(PROJECT_DIR, item):
        continue
    
    src = os.path.join(PROJECT_DIR, item)
    dst = os.path.join(temp_dir, item)
    
    if os.path.isdir(src):
        shutil.copytree(src, dst, ignore=lambda d, files: [f for f in files if should_exclude(d, f)])
    else:
        shutil.copy2(src, dst)

# Criar diretórios vazios necessários
os.makedirs(os.path.join(temp_dir, 'instance'), exist_ok=True)
os.makedirs(os.path.join(temp_dir, 'uploads'), exist_ok=True)
os.makedirs(os.path.join(temp_dir, 'outputs'), exist_ok=True)
os.makedirs(os.path.join(temp_dir, 'logs'), exist_ok=True)

# Criar arquivo de credenciais separado
creds_file = os.path.join(temp_dir, 'CREDENCIAIS_ADMIN.txt')
with open(creds_file, 'w', encoding='utf-8') as f:
    f.write("=" * 50 + "\n")
    f.write("CREDENCIAIS DE ACESSO - SISTEMA SBACEM\n")
    f.write("=" * 50 + "\n\n")
    f.write("ADMINISTRADOR PADRÃO:\n")
    f.write("-" * 30 + "\n")
    f.write("Email: admin@sbacem.org.br\n")
    f.write("Senha: admin123\n\n")
    f.write("⚠️ IMPORTANTE:\n")
    f.write("Altere esta senha imediatamente após o primeiro acesso!\n\n")
    f.write("Para alterar a senha:\n")
    f.write("1. Faça login com as credenciais acima\n")
    f.write("2. Acesse Menu > Configurações > Usuários\n")
    f.write("3. Edite o usuário admin\n")
    f.write("4. Defina uma nova senha segura (mínimo 8 caracteres)\n")
    f.write("=" * 50 + "\n")

print(f"Arquivo de credenciais criado: {creds_file}")

# Criar ZIP
zip_path = os.path.join(OUTPUT_DIR, zip_name)
print(f"\nCriando ZIP: {zip_path}.zip")
shutil.make_archive(zip_path, 'zip', temp_dir)

# Limpar temporário
shutil.rmtree(temp_dir)

print("\n" + "=" * 50)
print("✅ PACOTE DE ENTREGA CRIADO COM SUCESSO!")
print("=" * 50)
print(f"\nArquivo: {zip_path}.zip")
print(f"Tamanho: {os.path.getsize(zip_path + '.zip') / 1024 / 1024:.2f} MB")
print("\nConteúdo do pacote:")
print("  - Código fonte completo")
print("  - Banco de dados VAZIO (será criado automaticamente)")
print("  - CREDENCIAIS_ADMIN.txt (entregar separadamente)")
print("  - CONFIGURAR_EMAIL.md (guia de configuração de email)")
print("  - Documentação atualizada")
print("\n⚠️ O arquivo CREDENCIAIS_ADMIN.txt está dentro do ZIP.")
print("   Recomenda-se enviá-lo separadamente por questões de segurança.")
