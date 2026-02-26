
import sys
import os
# Adiciona o diretório shared ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from gerador_ecad_titulares import gerar_arquivo_titulares

def test_geracao():
    test_data = [
        {
            'cpf': '12345678901',
            'nome': 'JOAO DA SILVA TESTE',
            'rua': 'RUA DAS FLORES',
            'numero': '123',
            'bairro': 'CENTRO',
            'cidade': 'SAO PAULO',
            'uf': 'SP',
            'cep': '01001000'
        },
        {
            'cpf': '98765432100',
            'nome': 'MARIA SOUZA TESTE',
            'rua': 'AVENIDA PAULISTA',
            'numero': '1000',
            'bairro': 'BELA VISTA',
            'cidade': 'SAO PAULO',
            'uf': 'SP',
            'cep': '01310100'
        }
    ]
    
    output_path = os.path.join(os.path.dirname(__file__), 'outputs', 'teste_titulares_0660.txt')
    result = gerar_arquivo_titulares(test_data, output_path)
    
    print(f"Arquivo gerado em: {result['path']}")
    print(f"Total de registros: {result['count']}")
    
    with open(output_path, 'r', encoding='latin-1') as f:
        content = f.read()
        print("\nConteúdo do arquivo:")
        print(content)

if __name__ == "__main__":
    test_geracao()
