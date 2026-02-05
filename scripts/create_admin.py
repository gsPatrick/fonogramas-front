import sys
import os

# Adiciona o diretório raiz ao path para importar app e models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User

def create_admin():
    with app.app_context():
        email = 'admin@sbacem.org.br'
        print(f"Verificando existência do administrador: {email}...")
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print("Administrador não encontrado. Criando...")
            user = User(
                nome='Administrador',
                email=email,
                role='admin',
                associacao='SBACEM',
                ativo=True
            )
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()
            print("✅ Administrador criado com sucesso!")
            print(f"   Email: {email}")
            print(f"   Senha: admin123")
        else:
            # Garante que é admin e está ativo
            changed = False
            if user.role != 'admin':
                user.role = 'admin'
                changed = True
            if not user.ativo:
                user.ativo = True
                changed = True
            
            if changed:
                db.session.commit()
                print("✅ Usuário existente atualizado para Admin/Ativo.")
            else:
                print("✅ Administrador já existe e está configurado.")

if __name__ == '__main__':
    create_admin()
