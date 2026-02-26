
import os
from dotenv import load_dotenv

def check_env():
    load_dotenv()
    
    keys_to_check = {
        'Clicksign': ['CLICKSIGN_ACCESS_TOKEN', 'CLICKSIGN_BASE_URL'],
        'Redes Sociais': ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'YOUTUBE_CLIENT_ID'],
        'TOTVS': ['TOTVS_API_URL', 'TOTVS_API_KEY'],
        'Core': ['DATABASE_URL', 'SECRET_KEY']
    }
    
    print("="*50)
    print("HEALTH CHECK: VARIÁVEIS DE AMBIENTE (PRODUÇÃO)")
    print("="*50)
    
    all_ok = True
    
    for category, keys in keys_to_check.items():
        print(f"\n[{category}]")
        for key in keys:
            val = os.getenv(key)
            if val:
                # Mostrar apenas que existe e o comprimento/máscara básica para segurança
                status = "✅ PREENCHIDA"
                masked = val[:3] + "*" * (len(val)-6) + val[-3:] if len(val) > 6 else "***"
                if key == 'DATABASE_URL': masked = "HIDDEN" # Muito sensível
                print(f"  - {key.ljust(25)}: {status} ({masked})")
            else:
                status = "❌ AUSENTE OU VAZIA"
                print(f"  - {key.ljust(25)}: {status}")
                all_ok = False
                
    print("\n" + "="*50)
    if all_ok:
        print("VEREDITO: AMBIENTE CONFIGURADO CORRETAMENTE.")
    else:
        print("VEREDITO: ATENÇÃO! EXISTEM CHAVES FALTANDO NO .ENV.")
    print("="*50)

if __name__ == "__main__":
    check_env()
