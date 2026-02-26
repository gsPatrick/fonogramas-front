
import paramiko
import os
import re

# Configuration from deploy_new_satellites.py
HOST = "129.121.39.128"
PORT = 22022
USER = "root"
PASSWORD = "Senhanova#123"

def remote_execute(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    return exit_status, out, err

def mask_val(val):
    if not val: return "❌ AUSENTE"
    if len(val) > 8:
        return f"✅ PREENCHIDA ({val[:3]}...{val[-3:]})"
    return "✅ PREENCHIDA (***)"

def check_production():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("="*60)
    print("PRODUÇÃO: HEALTH CHECK REMOTO (129.121.39.128)")
    print("="*60)
    
    try:
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
        print("Conectado ao servidor via SSH.\n")
        
        paths = {
            "Fonogramas API": "/opt/fonogramas-api",
            "Cadastro API (Nest)": "/opt/cadastro-api/apps/api"
        }
        
        keys_to_check = [
            'CLICKSIGN_ACCESS_TOKEN', 'CLICKSIGN_BASE_URL',
            'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'YOUTUBE_CLIENT_ID',
            'TOTVS_API_URL', 'TOTVS_API_KEY', 'TOTVS_BASE_URL', 'TOTVS_TOKEN',
            'DATABASE_URL', 'SECRET_KEY'
        ]
        
        for app_name, path in paths.items():
            print(f"--- {app_name} ({path}) ---")
            
            # 1. Verificar arquivo .env
            status, out, err = remote_execute(ssh, f"cat {path}/.env")
            if status == 0:
                print("Lendo .env remoto:")
                env_lines = out.splitlines()
                for key in keys_to_check:
                    match = next((l for l in env_lines if l.startswith(f"{key}=")), None)
                    if match:
                        val = match.split('=', 1)[1].strip().strip('"').strip("'")
                        print(f"  - {key.ljust(25)}: {mask_val(val)}")
                    else:
                        print(f"  - {key.ljust(25)}: ❌ NÃO ENCONTRADA NO .ENV")
            else:
                print(f"⚠️ Erro ao acessar .env em {path}")

            # 2. Verificar processos reais (Caso estejam em variaveis de sistema)
            print("\nVerificando variáveis de processo (Ambiente Ativo):")
            # Para Python/Gunicorn: cat /proc/<pid>/environ
            # Para Nest/PM2: pm2 env <id>
            
            if "Fonogramas" in app_name:
                _, out_pid, _ = remote_execute(ssh, "pgrep -f gunicorn")
                if out_pid:
                    pid = out_pid.splitlines()[0]
                    _, out_env, _ = remote_execute(ssh, f"strings /proc/{pid}/environ")
                    for key in keys_to_check:
                        match = next((l for l in out_env.splitlines() if l.startswith(key)), None)
                        if match:
                            val = match.split('=', 1)[1].strip()
                            print(f"  - {key.ljust(25)} (Proc): {mask_val(val)}")
            
            elif "Cadastro" in app_name:
                _, out_pm2, _ = remote_execute(ssh, "pm2 jlist")
                # pm2 jlist da um JSON, mas strings via pm2 show tbm funciona
                _, out_env, _ = remote_execute(ssh, "pm2 show cadastro-api")
                for key in keys_to_check:
                    if key in out_env:
                        # Extração rústica do pm2 show
                        print(f"  - {key.ljust(25)} (PM2): ✅ PRESENTE (Confirmação visual requerida)")
            
            print("\n")

        ssh.close()
    except Exception as e:
        print(f"❌ Falha na conexão ou execução remota: {str(e)}")

if __name__ == "__main__":
    check_production()
