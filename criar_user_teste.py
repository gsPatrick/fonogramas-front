import sys
import os

# Adicionar o diretório atual ao path para importar modulos do Flask
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User

def criar_usuario():
    with app.app_context():
        # Verifica se o usuario ja existe
        email_teste = 'teste@sbacem.org.br'
        user = User.query.filter_by(email=email_teste).first()
        
        if user:
            print(f"Usuário {email_teste} já existe. Atualizando senha para 'Senha123!'.")
            user.set_password('Senha123!')
        else:
            print(f"Criando novo usuário {email_teste}...")
            user = User(
                email=email_teste,
                nome='Usuário de Teste Fonogramas',
                role='admin',
                ativo=True
            )
            user.set_password('Senha123!')
            db.session.add(user)
            
        db.session.commit()
        print("Operação concluída com sucesso!")

if __name__ == '__main__':
    criar_usuario()
