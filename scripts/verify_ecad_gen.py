
import sys
import os
import types
from datetime import datetime

# Imporant hack to import modules from parent directory
sys.path.append(os.getcwd())

# --- MONKEY PATCHING STARTS HERE ---
# Create a mock 'models' module
mock_models = types.ModuleType('models')

class MockObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __getattr__(self, name):
        return None # Default to None for missing attributes

class Fonograma(MockObj):
    def __init__(self):
        self.autores_list = []
        self.editoras_list = []
        self.interpretes_list = []
        self.musicos_list = []
        self.cod_interno = None
        self.cod_obra = None
        self.isrc = None
        self.titulo = None
        self.titulo_obra = None
        self.duracao = None
        self.ano_grav = None
        self.ano_lanc = None
        self.data_lanc = None
        self.flag_nacional = None
        self.genero = None
        self.idioma = None
        self.prod_nome = None
        self.prod_doc = None
        self.prod_perc = None
        self.prod_assoc = None
        self.prod_fantasia = None
        self.prod_endereco = None
        self.tipo_lanc = None
        self.album = None
        self.faixa = None
        self.selo = None
        self.formato = None
        self.pais = None
        self.pais_origem = None
        self.paises_adicionais = None
        self.assoc_gestao = None
        self.territorio = None
        self.tipos_exec = None

class Autor(MockObj):
    pass
class Editora(MockObj):
    pass
class Interprete(MockObj):
    pass

# Populate the mock module
mock_models.Fonograma = Fonograma
mock_models.Autor = Autor
mock_models.Editora = Editora
mock_models.Interprete = Interprete

# Inject into sys.modules
sys.modules['models'] = mock_models

# --- NOW WE CAN IMPORT ---
from shared.gerador_ecad import gerar_txt_ecad

def create_mock_fonograma():
    # Mock data based on reference file line 2185 (ID 1425872)
    fono = Fonograma()
    fono.id = 1425872
    fono.cod_interno = "064294797"
    fono.cod_obra = "410079"
    fono.isrc = "BCLF32600024"
    fono.titulo = "EU SEM VOCE"
    fono.titulo_obra = "EU SEM VOCE"
    fono.duracao = "228" # seconds
    fono.ano_grav = 2026
    fono.ano_lanc = 2026
    fono.data_lanc = "01/01/2026"
    fono.flag_nacional = "NACIONAL"
    fono.genero = "SAMBA" # code 14
    fono.idioma = "PT"
    
    # Mock Autor
    autor = Autor()
    autor.nome = "Ruben Jose Marques Gomes"
    autor.cpf = "651262073"
    autor.funcao = "Compositor"
    autor.percentual = 100.0
    autor.cae_ipi = "0033738984"
    fono.autores_list = [autor]
    
    # Mock Produtor
    fono.prod_nome = "Luiz Claudio de Freitas Silva"
    fono.prod_doc = "08563224743"
    fono.prod_perc = 100.0
    fono.prod_assoc = "SBACEM"
    
    # Mock Interprete
    interp = Interprete()
    interp.nome = "Luiz Claudio de Freitas Silva" # Same name as producer in reference
    interp.doc = "08563224743"
    interp.categoria = "PRINCIPAL"
    interp.percentual = 100.0
    interp.associacao = "SBACEM"
    fono.interpretes_list = [interp]
    
    return [fono]

def verify():
    fonogramas = create_mock_fonograma()
    output_file = "verify_output_ecad.txt"
    
    try:
        result = gerar_txt_ecad(fonogramas, output_file)
        print(f"Generated file: {result['arquivo']}")
        
        with open(output_file, 'r', encoding='latin-1') as f:
            lines = [l.rstrip() for l in f.readlines()]
            
        print(f"Total lines: {len(lines)}")
        print("Lines generated:")
        
        for i, line in enumerate(lines):
            print(f"Line {i+1} (len={len(line)}):")
            print(line)
            if "FON1" in line:
                print("Ruler 0-9:")
                print("0123456789"*10)
                print("Ruler 10s:")
                print("00000000001111111111222222222233333333334444444444")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
