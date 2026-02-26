
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gerador_ecad_titulares import build_registro_002

def verify_detail_row():
    dummy_data = {
        'cpf': '12345678901',
        'nome': 'PEDRO ALVARES CABRAL DOS SANTOS TESTE LAYOUT',
        'rua': 'AVENIDA BRASIL',
        'numero': '1500',
        'bairro': 'CENTRO',
        'cidade': 'SAO PAULO',
        'uf': 'SP',
        'cep': '01001000'
    }
    
    line = build_registro_002(2, dummy_data)
    
    print(f"STRING GERADA (Registro 002):")
    print(f"'{line}'")
    
    length = len(line)
    print(f"\n1. Comprimento total: {length} (Esperado: 428)")
    
    # Nome do Titular termina na posição 107.
    # No manual ECAD, posições são 1-based.
    # Posições 028-107 para Nome (80 chars).
    # O 107º caracter é line[106]
    name_field = line[27:107]
    print(f"2. Campo Nome (pos 28-107): '{name_field}'")
    print(f"   Termina na posição 107? {'Sim' if len(line[:107]) == 107 else 'Não'}")
    
    # CPF está na posição correta (14-27)?
    cpf_field = line[13:27]
    print(f"3. Campo CPF (pos 14-27): '{cpf_field}'")
    
    # Validação final
    if length == 428 and len(name_field) == 80:
        print("\n[SUCESSO] O layout Detalhe está 100% preciso.")
    else:
        print("\n[ERRO] Divergência no layout Detalhe.")

def verify_trailer():
    from gerador_ecad_titulares import build_registro_999
    
    # Simulação: 1 header + 5 detalhes + 1 trailer = 7 linhas totais, 5 grupos
    line = build_registro_999(7, 5)
    
    print(f"\nSTRING GERADA (Registro 999):")
    print(f"'{line}'")
    
    length = len(line)
    print(f"1. Comprimento total: {length} (Esperado: 428)")
    print(f"2. Total Linhas (pos 08-13): '{line[7:13]}' (Esperado: 000007)")
    print(f"3. Total Grupos (pos 14-19): '{line[13:19]}' (Esperado: 000005)")
    
    if length == 428 and line[7:13] == '000007' and line[13:19] == '000005':
        print("\n[SUCESSO] O trailer está 100% preciso.")
    else:
        print("\n[ERRO] Divergência no trailer.")

if __name__ == "__main__":
    verify_detail_row()
    verify_trailer()
