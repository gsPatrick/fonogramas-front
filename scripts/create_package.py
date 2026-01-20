import zipfile
import os

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        # Ignorar pastas indesejadas
        if 'venv' in root or '__pycache__' in root or '.git' in root or '.gemini' in root or 'arquivos_nao_usados' in root:
            continue
            
        for file in files:
            # Ignorar arquivos indesejados
            if file == 'FONOGRAMA_ENTREGA_FINAL.zip' or file.endswith('.pyc') or file.startswith('backup_') or file.startswith('temp_'):
                continue
                
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, path)
            ziph.write(file_path, arcname)

if __name__ == '__main__':
    with zipfile.ZipFile('FONOGRAMA_ENTREGA_FINAL.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir('.', zipf)
    print("✅ FONOGRAMA_ENTREGA_FINAL.zip criado com sucesso!")
