import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User
import csv

def generate_cpf():
    """Gera um CPF válido para testes"""
    def calc_digit(digits):
        s = sum(d * w for d, w in zip(digits, range(len(digits) + 1, 1, -1)))
        r = s % 11
        return 0 if r < 2 else 11 - r

    digits = [random.randint(0, 9) for _ in range(9)]
    digits.append(calc_digit(digits))
    digits.append(calc_digit(digits))
    return ''.join(map(str, digits))

def generate_cnpj():
    """Gera um CNPJ válido para testes"""
    def calc_digit(digits, weights):
        s = sum(d * w for d, w in zip(digits, weights))
        r = s % 11
        return 0 if r < 2 else 11 - r

    base = [random.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    
    # Pesos para 1º dígito
    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = calc_digit(base, w1)
    base.append(d1)
    
    # Pesos para 2º dígito
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d2 = calc_digit(base, w2)
    base.append(d2)
    
    return ''.join(map(str, base))

def setup():
    with app.app_context():
        # 1. Create Test User (Idempotent)
        user = User.query.filter_by(email='musico@teste.com').first()
        if not user:
            user = User(
                nome='Músico Teste',
                email='musico@teste.com',
                role='usuario',
                associacao='ABRAMUS',
                cpf_cnpj=generate_cpf()
            )
            user.set_password('123456')
            db.session.add(user)
            db.session.commit()
            print("✅ Usuário 'musico@teste.com' verificado.")
        
        # Gerar documentos válidos para o CSV
        cpf_vinicius = generate_cpf()
        cpf_tom = generate_cpf()
        cpf_joao = generate_cpf()
        cpf_astrud = generate_cpf()
        cpf_jorge = generate_cpf()
        cpf_sergio = generate_cpf()
        cnpj_prod = generate_cnpj()

        # 2. Create Realistic CSV (Corrected Validations)
        csv_path = os.path.join(os.getcwd(), 'fonograma_realista_teste.csv')
        headers = [
            'ISRC', 'TÍTULO', 'VERSÃO', 'DURAÇÃO', 'ANO_GRAVAÇÃO', 'ANO_LANÇAMENTO',
            'IDIOMA', 'GÊNERO', 'TÍTULO_OBRA', 'CÓDIGO_OBRA', 
            'AUTORES', 'INTÉRPRETES',
            'PRODUTOR_NOME', 'PRODUTOR_DOCUMENTO', 'PRODUTOR_PERCENTUAL', 'PRODUTOR_ASSOCIAÇÃO',
            'TIPO_GRAVAÇÃO', 'TIPO_LANÇAMENTO'
        ]
        
        # Regra de Conexos: Interpretes + Musicos + Produtor = 100%
        # Exemplo 1: Produtor 50%, Intérpretes 50%
        # Exemplo 2: Produtor 40%, Intérpretes 60%
        
        data = [
            # Entry 1: Bossa Nova (Valid Genre), Remix (Valid Version)
            [
                'BRBIO2600001', 'Garota de Ipanema (Remix 2026)', 'remix', '03:45', '2026', '2026',
                'PT', 'Bossa Nova', 'Garota de Ipanema', '',
                # Autores: 50% + 50% = 100%
                f'Vinicius de Moraes|{cpf_vinicius}|LETRISTA|50;Tom Jobim|{cpf_tom}|COMPOSITOR|50',
                # Intérpretes: 25% + 25% = 50% (Total Conexos = 50% Interp + 50% Prod = 100%)
                f'João Gilberto|{cpf_joao}|PRINCIPAL|25|UBC;Astrud Gilberto|{cpf_astrud}|PRINCIPAL|25|ABRAMUS',
                'Leandro Produções Ltda', cnpj_prod, '50', 'ABRAMUS',
                'Original', 'SINGLE'
            ],
            # Entry 2: MPB (Valid Genre instead of Samba), Original (Valid Version)
            [
                'BRBIO2600002', 'Mas Que Nada (Radio Edit)', 'original', '02:30', '2025', '2026',
                'PT', 'MPB', 'Mas Que Nada', '',
                # Autores: 100%
                f'Jorge Ben Jor|{cpf_jorge}|COMPOSITOR|100',
                # Intérpretes: 60% (Total Conexos = 60% Interp + 40% Prod = 100%)
                f'Sergio Mendes|{cpf_sergio}|PRINCIPAL|60|SOCINPRO',
                'Leandro Produções Ltda', cnpj_prod, '40', 'ABRAMUS',
                'Original', 'ALBUM'
            ]
        ]

        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            writer.writerows(data)
        
        print(f"✅ Arquivo CSV 'Golden' gerado com CPFs, CNPJs e percentuais válidos: {csv_path}")

if __name__ == '__main__':
    setup()
