
import requests
import io

URL = "http://localhost:5001/api/propostas"

def test_submit():
    data = {
        'nome_completo': 'Teste Smoke',
        'cpf': '12345678901',
        'email': 'teste@sbacem.org.br',
        'banco': 'ITAU'
    }
    
    files = {
        'identificacao': ('rg.pdf', io.BytesIO(b"dummy pdf content"), 'application/pdf')
    }
    
    try:
        print(f"Testando POST {URL}...")
        # Note: In a real environment, you'd need the Flask app running.
        # This is for documentation of how to test.
        # response = requests.post(URL, data=data, files=files)
        # print(response.json())
        print("Teste de envio preparado. Requer Flask rodando em :5001.")
    except Exception as e:
        print(f"Erro no teste: {e}")

if __name__ == "__main__":
    test_submit()
