"""
Processador de retorno ECAD
Importa e processa arquivos de retorno do ECAD
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List
from models import db, Fonograma, EnvioECAD, RetornoECAD, HistoricoFonograma


def importar_retorno_ecad(arquivo_path: str, envio_id: int) -> Dict:
    """
    Importa arquivo de retorno do ECAD
    
    Args:
        arquivo_path: Caminho do arquivo de retorno
        envio_id: ID do envio relacionado
        
    Returns:
        Dict com dados processados do retorno
    """
    
    # Detectar formato do arquivo
    extensao = os.path.splitext(arquivo_path)[1].lower()
    
    try:
        if extensao in ['.xlsx', '.xls']:
            df = pd.read_excel(arquivo_path)
        elif extensao == '.csv':
            df = pd.read_csv(arquivo_path, encoding='utf-8')
        elif extensao == '.txt':
            # Tentar ler como delimitado por pipe ou tab
            try:
                df = pd.read_csv(arquivo_path, sep='|', encoding='utf-8')
            except:
                df = pd.read_csv(arquivo_path, sep='\t', encoding='utf-8')
        else:
            return {
                'sucesso': False,
                'erro': f'Formato de arquivo não suportado: {extensao}'
            }
        
        # Normalizar nomes de colunas (remover espaços, converter para maiúsculas)
        df.columns = df.columns.str.strip().str.upper()
        
        # Mapear colunas possíveis do ECAD
        # Nota: Ajustar conforme formato real do retorno ECAD
        mapeamento_colunas = {
            'ISRC': ['ISRC', 'CODIGO_ISRC', 'COD_ISRC'],
            'STATUS': ['STATUS', 'SITUACAO', 'RESULTADO'],
            'CODIGO_ERRO': ['CODIGO_ERRO', 'COD_ERRO', 'ERRO_COD', 'CODIGO'],
            'MENSAGEM': ['MENSAGEM', 'MENSAGEM_ERRO', 'DESCRICAO', 'OBSERVACAO'],
            'COD_ECAD': ['COD_ECAD', 'CODIGO_ECAD', 'ID_ECAD']
        }
        
        # Identificar colunas presentes
        colunas_encontradas = {}
        for campo, possiveis in mapeamento_colunas.items():
            for possivel in possiveis:
                if possivel in df.columns:
                    colunas_encontradas[campo] = possivel
                    break
        
        # Validar se tem pelo menos ISRC e STATUS
        if 'ISRC' not in colunas_encontradas or 'STATUS' not in colunas_encontradas:
            return {
                'sucesso': False,
                'erro': 'Arquivo de retorno não contém colunas obrigatórias (ISRC e STATUS)',
                'colunas_encontradas': list(df.columns)
            }
        
        # Processar linhas
        retornos_processados = []
        for _, row in df.iterrows():
            isrc = str(row[colunas_encontradas['ISRC']]).strip()
            status = str(row[colunas_encontradas['STATUS']]).strip().upper()
            
            # Extrair outros campos se existirem
            codigo_erro = None
            mensagem = None
            cod_ecad = None
            
            if 'CODIGO_ERRO' in colunas_encontradas:
                codigo_erro = str(row[colunas_encontradas['CODIGO_ERRO']]) if pd.notna(row[colunas_encontradas['CODIGO_ERRO']]) else None
            
            if 'MENSAGEM' in colunas_encontradas:
                mensagem = str(row[colunas_encontradas['MENSAGEM']]) if pd.notna(row[colunas_encontradas['MENSAGEM']]) else None
            
            if 'COD_ECAD' in colunas_encontradas:
                cod_ecad = str(row[colunas_encontradas['COD_ECAD']]) if pd.notna(row[colunas_encontradas['COD_ECAD']]) else None
            
            retornos_processados.append({
                'isrc': isrc,
                'status': status,
                'codigo_erro': codigo_erro,
                'mensagem': mensagem,
                'cod_ecad': cod_ecad
            })
        
        return {
            'sucesso': True,
            'total_linhas': len(retornos_processados),
            'retornos': retornos_processados
        }
        
    except Exception as e:
        return {
            'sucesso': False,
            'erro': f'Erro ao processar arquivo: {str(e)}'
        }


def processar_retorno(retorno_data: Dict, envio_id: int) -> Dict:
    """
    Processa dados do retorno e atualiza banco de dados
    
    Args:
        retorno_data: Dados do retorno (resultado de importar_retorno_ecad)
        envio_id: ID do envio relacionado
        
    Returns:
        Dict com resultado do processamento
    """
    
    if not retorno_data.get('sucesso'):
        return retorno_data
    
    # Buscar envio
    envio = EnvioECAD.query.get(envio_id)
    if not envio:
        return {
            'sucesso': False,
            'erro': f'Envio {envio_id} não encontrado'
        }
    
    aceitos = 0
    recusados = 0
    nao_encontrados = []
    erros = []
    
    try:
        for ret in retorno_data['retornos']:
            isrc = ret['isrc']
            
            # Buscar fonograma pelo ISRC
            fonograma = Fonograma.query.filter_by(isrc=isrc).first()
            
            if not fonograma:
                nao_encontrados.append(isrc)
                continue
            
            # Interpretar status
            status_ecad = interpretar_status_retorno(ret['status'])
            
            # Criar registro de retorno
            retorno_ecad = RetornoECAD(
                envio_id=envio_id,
                fonograma_id=fonograma.id,
                data_retorno=datetime.utcnow(),
                status_ecad=status_ecad,
                codigo_erro=ret.get('codigo_erro'),
                mensagem_erro=ret.get('mensagem'),
                cod_ecad_gerado=ret.get('cod_ecad')
            )
            db.session.add(retorno_ecad)
            
            # Atualizar status do fonograma
            status_anterior = fonograma.status_ecad
            fonograma.status_ecad = status_ecad
            
            # Se aceito, atualizar cod_ecad
            if status_ecad == 'ACEITO' and ret.get('cod_ecad'):
                fonograma.cod_ecad = ret['cod_ecad']
            
            # Registrar no histórico
            historico = HistoricoFonograma(
                fonograma_id=fonograma.id,
                data_alteracao=datetime.utcnow(),
                tipo_alteracao='RETORNO',
                campo_alterado='status_ecad',
                valor_anterior=status_anterior,
                valor_novo=status_ecad,
                motivo=f'Retorno do envio {envio.protocolo or envio.id}',
                detalhes=f'Código: {ret.get("codigo_erro")}, Mensagem: {ret.get("mensagem")}'
            )
            db.session.add(historico)
            
            # Contabilizar
            if status_ecad == 'ACEITO':
                aceitos += 1
            elif status_ecad == 'RECUSADO':
                recusados += 1
        
        # Atualizar status do envio
        envio.status = 'PROCESSADO'
        envio.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'sucesso': True,
            'total_processados': len(retorno_data['retornos']),
            'aceitos': aceitos,
            'recusados': recusados,
            'nao_encontrados': nao_encontrados,
            'envio_id': envio_id
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'sucesso': False,
            'erro': f'Erro ao processar retorno: {str(e)}'
        }


def interpretar_status_retorno(status: str) -> str:
    """
    Interpreta status retornado pelo ECAD
    
    Args:
        status: Status bruto do retorno
        
    Returns:
        Status normalizado (ACEITO ou RECUSADO)
    """
    
    status = status.upper().strip()
    
    # Mapeamento de possíveis valores
    aceitos = ['ACEITO', 'APROVADO', 'OK', 'SUCESSO', 'IMPORTADO', 'CADASTRADO']
    recusados = ['RECUSADO', 'REJEITADO', 'ERRO', 'FALHA', 'INVALIDO', 'NEGADO']
    
    for termo in aceitos:
        if termo in status:
            return 'ACEITO'
    
    for termo in recusados:
        if termo in status:
            return 'RECUSADO'
    
    # Se não identificar, considerar recusado por segurança
    return 'RECUSADO'


def interpretar_codigo_erro(codigo: str) -> str:
    """
    Traduz código de erro ECAD para mensagem legível
    
    Nota: Este mapeamento deve ser atualizado conforme
    documentação oficial do ECAD
    
    Args:
        codigo: Código de erro do ECAD
        
    Returns:
        Mensagem traduzida
    """
    
    if not codigo:
        return ''
    
    # Mapeamento de códigos conhecidos (exemplo - ajustar conforme documentação)
    mapeamento = {
        'E001': 'ISRC inválido ou duplicado',
        'E002': 'Campos obrigatórios faltando',
        'E003': 'Percentuais não somam 100%',
        'E004': 'CPF/CNPJ inválido',
        'E005': 'Obra não cadastrada',
        'E006': 'Autor não cadastrado',
        'E007': 'Produtor não cadastrado',
        'E008': 'Formato de data inválido',
        'E009': 'Duração inválida',
        'E010': 'Gênero não reconhecido',
    }
    
    return mapeamento.get(codigo, f'Código de erro: {codigo}')


def obter_fonogramas_para_reenvio(envio_id: int) -> List[int]:
    """
    Retorna IDs dos fonogramas recusados em um envio
    
    Args:
        envio_id: ID do envio
        
    Returns:
        Lista de IDs de fonogramas recusados
    """
    
    retornos_recusados = RetornoECAD.query.filter_by(
        envio_id=envio_id,
        status_ecad='RECUSADO'
    ).all()
    
    return [r.fonograma_id for r in retornos_recusados]
