"""
Mﾃｳdulo de processamento e parsing de dados de fonogramas
"""

import pandas as pd
import csv
import chardet
from typing import List, Dict, Optional, Tuple
from validador import (
    validar_cpf, validar_cnpj, validar_isrc, validar_duracao,
    validar_percentuais_conexos, validar_percentuais_autorais,
    validar_percentuais_editoras, validar_genero, validar_funcao_autor,
    validar_categoria_interprete, validar_tipo_musico, validar_associacao,
    validar_tipo_lancamento, validar_formato, validar_situacao,
    validar_territorio, validar_tipo_execucao, validar_prioridade,
    validar_tipo_documento, validar_ano, validar_data, validar_versao,
    validar_idioma, limpar_documento, GENEROS
)


def parse_autores(campo: str) -> List[Dict]:
    """
    Entrada: "Joﾃ｣o|12345678901|COMPOSITOR|50;Maria|98765432100|LETRISTA|50"
    Saﾃｭda: [
        {"nome": "Joﾃ｣o", "cpf": "12345678901", "funcao": "COMPOSITOR", "percentual": 50},
        {"nome": "Maria", "cpf": "98765432100", "funcao": "LETRISTA", "percentual": 50}
    ]
    """
    if not campo or pd.isna(campo):
        return []
    
    autores = []
    registros = str(campo).split(';')
    
    for registro in registros:
        registro = registro.strip()
        if not registro:
            continue
        
        partes = registro.split('|')
        if len(partes) >= 4:
            try:
                autor = {
                    "nome": partes[0].strip(),
                    "cpf": limpar_documento(partes[1]),
                    "funcao": partes[2].strip().upper(),
                    "percentual": float(partes[3].strip().replace('%', '').replace(',', '.'))
                }
                autores.append(autor)
            except (ValueError, IndexError):
                continue
    
    return autores


def parse_interpretes(campo: str) -> List[Dict]:
    """
    Entrada: "Joﾃ｣o|12345678901|PRINCIPAL|50|ABRAMUS;Maria|98765432100|COADJUVANTE|50|UBC"
    Saﾃｭda: [
        {"nome": "Joﾃ｣o", "doc": "12345678901", "categoria": "PRINCIPAL", "percentual": 50, "associacao": "ABRAMUS"},
        ...
    ]
    """
    if not campo or pd.isna(campo):
        return []
    
    interpretes = []
    registros = str(campo).split(';')
    
    for registro in registros:
        registro = registro.strip()
        if not registro:
            continue
        
        partes = registro.split('|')
        if len(partes) >= 4:
            try:
                interprete = {
                    "nome": partes[0].strip(),
                    "doc": limpar_documento(partes[1]),
                    "categoria": partes[2].strip().upper(),
                    "percentual": float(partes[3].strip().replace('%', '').replace(',', '.'))
                }
                if len(partes) >= 5:
                    interprete["associacao"] = partes[4].strip().upper()
                else:
                    interprete["associacao"] = ""
                interpretes.append(interprete)
            except (ValueError, IndexError):
                continue
    
    return interpretes


def parse_musicos(campo: str) -> List[Dict]:
    """
    Entrada: "Joﾃ｣o|12345678901|BATERIA|FIXO|25;Maria|98765432100|GUITARRA|EVENTUAL|15"
    Saﾃｭda: [
        {"nome": "Joﾃ｣o", "cpf": "12345678901", "instrumento": "BATERIA", "tipo": "FIXO", "percentual": 25},
        ...
    ]
    """
    if not campo or pd.isna(campo):
        return []
    
    musicos = []
    registros = str(campo).split(';')
    
    for registro in registros:
        registro = registro.strip()
        if not registro:
            continue
        
        partes = registro.split('|')
        if len(partes) >= 5:
            try:
                musico = {
                    "nome": partes[0].strip(),
                    "cpf": limpar_documento(partes[1]),
                    "instrumento": partes[2].strip(),
                    "tipo": partes[3].strip().upper(),
                    "percentual": float(partes[4].strip().replace('%', '').replace(',', '.'))
                }
                musicos.append(musico)
            except (ValueError, IndexError):
                continue
    
    return musicos


def parse_editoras(campo: str) -> List[Dict]:
    """
    Entrada: "Editora A|12345678000190|50;Editora B|98765432000100|50"
    Saﾃｭda: [
        {"nome": "Editora A", "cnpj": "12345678000190", "percentual": 50},
        ...
    ]
    """
    if not campo or pd.isna(campo):
        return []
    
    editoras = []
    registros = str(campo).split(';')
    
    for registro in registros:
        registro = registro.strip()
        if not registro:
            continue
        
        partes = registro.split('|')
        if len(partes) >= 3:
            try:
                editora = {
                    "nome": partes[0].strip(),
                    "cnpj": limpar_documento(partes[1]),
                    "percentual": float(partes[2].strip().replace('%', '').replace(',', '.'))
                }
                editoras.append(editora)
            except (ValueError, IndexError):
                continue
    
    return editoras


def parse_documentos(campo: str) -> List[Dict]:
    """
    Entrada: "DECLARACAO|REF123|01/01/2024;CONTRATO_CESSAO|REF456|15/03/2024"
    Saﾃｭda: [
        {"tipo": "DECLARACAO", "referencia": "REF123", "data": "01/01/2024"},
        ...
    ]
    """
    if not campo or pd.isna(campo):
        return []
    
    documentos = []
    registros = str(campo).split(';')
    
    for registro in registros:
        registro = registro.strip()
        if not registro:
            continue
        
        partes = registro.split('|')
        if len(partes) >= 3:
            try:
                documento = {
                    "tipo": partes[0].strip().upper(),
                    "referencia": partes[1].strip(),
                    "data": partes[2].strip()
                }
                documentos.append(documento)
            except (ValueError, IndexError):
                continue
    
    return documentos


def detectar_encoding(arquivo_path: str) -> str:
    """
    Detecta encoding do arquivo automaticamente
    """
    try:
        with open(arquivo_path, 'rb') as f:
            raw_data = f.read(50000)  # Lﾃｪ primeiros 50KB
            resultado = chardet.detect(raw_data)
            encoding_detectado = resultado.get('encoding', 'utf-8')
            # Confianﾃｧa mﾃｭnima de 70%
            if resultado.get('confidence', 0) < 0.7:
                encoding_detectado = 'utf-8'
            return encoding_detectado
    except Exception:
        return 'utf-8'


def detectar_delimitador(arquivo_path: str, encoding: str = 'utf-8') -> str:
    """
    Detecta delimitador do CSV automaticamente
    """
    try:
        with open(arquivo_path, 'r', encoding=encoding, errors='ignore') as f:
            sample = f.read(2048)  # Lﾃｪ primeiros 2KB
            sniffer = csv.Sniffer()
            delimitador = sniffer.sniff(sample).delimiter
            return delimitador
    except Exception:
        return ','  # Default: vﾃｭrgula


def limpar_dados_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa dados do DataFrame (remove espaﾃｧos extras, normaliza, etc)
    """
    # Remove linhas completamente vazias
    df = df.dropna(how='all')
    
    # Limpa cada coluna
    for col in df.columns:
        # Converte para string e remove espaﾃｧos extras
        df[col] = df[col].astype(str).str.strip()
        # Normaliza quebras de linha dentro de cﾃｩlulas
        df[col] = df[col].str.replace('\n', ' ', regex=False)
        df[col] = df[col].str.replace('\r', ' ', regex=False)
        df[col] = df[col].str.replace('\t', ' ', regex=False)
        # Remove mﾃｺltiplos espaﾃｧos
        df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
        # Remove caracteres de controle invisﾃｭveis
        df[col] = df[col].str.replace(r'[\x00-\x1f\x7f-\x9f]', '', regex=True)
    
    return df


def ler_csv_com_fallback(arquivo_path: str) -> Tuple[pd.DataFrame, str, str]:
    """
    Lﾃｪ CSV tentando mﾃｺltiplos encodings e delimitadores
    Retorna: (DataFrame, encoding_usado, delimitador_usado)
    """
    erros_encoding = []
    
    # Tenta detectar encoding automaticamente
    encoding_detectado = detectar_encoding(arquivo_path)
    encodings = [encoding_detectado, 'utf-8', 'latin-1', 'windows-1252', 'iso-8859-1', 'cp1252']
    # Remove duplicatas mantendo ordem
    encodings = list(dict.fromkeys(encodings))
    
    for encoding in encodings:
        try:
            # Tenta detectar delimitador
            delimitador = detectar_delimitador(arquivo_path, encoding)
            delimitadores = [delimitador, ',', ';', '\t']
            delimitadores = list(dict.fromkeys(delimitadores))
            
            for delim in delimitadores:
                try:
                    df = pd.read_csv(
                        arquivo_path,
                        encoding=encoding,
                        delimiter=delim,
                        dtype=str,
                        on_bad_lines='skip',  # Pula linhas com erro
                        engine='python'  # Engine mais tolerante
                    )
                    
                    if len(df.columns) > 1:  # Verifica se tem mﾃｺltiplas colunas
                        # Limpa dados
                        df = limpar_dados_dataframe(df)
                        return df, encoding, delim
                        
                except Exception as e:
                    continue
                    
        except (UnicodeDecodeError, UnicodeError) as e:
            erros_encoding.append(f"{encoding}: {str(e)}")
            continue
        except Exception as e:
            continue
    
    # Se chegou aqui, nﾃ｣o conseguiu ler
    raise ValueError(
        f"Nﾃ｣o foi possﾃｭvel ler o arquivo CSV. "
        f"Tentou encodings: {', '.join(encodings)}. "
        f"Erros: {', '.join(erros_encoding[:3])}"
    )


def processar_csv(caminho_arquivo: str) -> tuple[pd.DataFrame, List[Dict]]:
    """
    Processa arquivo CSV e retorna DataFrame processado e lista de erros
    Suporta arquivos convertidos de PDF com detecﾃｧﾃ｣o automﾃ｡tica de encoding e delimitador
    """
    erros = []
    
    try:
        # Lﾃｪ o CSV com detecﾃｧﾃ｣o automﾃ｡tica de encoding e delimitador
        try:
            df, encoding_usado, delimitador_usado = ler_csv_com_fallback(caminho_arquivo)
        except ValueError as e:
            # Se falhar, tenta mﾃｩtodo simples como fallback
            try:
                df = pd.read_csv(caminho_arquivo, encoding='utf-8', dtype=str, on_bad_lines='skip')
                df = limpar_dados_dataframe(df)
                encoding_usado = 'utf-8'
                delimitador_usado = ','
            except Exception as e2:
                erros.append({
                    "linha": 0,
                    "campo": "arquivo",
                    "valor": "",
                    "erro": f"Erro ao ler arquivo CSV: {str(e)}. Detalhes: {str(e2)}"
                })
                return pd.DataFrame(), erros
        
        # Valida se tem colunas esperadas
        colunas_esperadas = ['isrc', 'titulo', 'duracao', 'ano_lanc', 'genero', 
                           'titulo_obra', 'autores', 'interpretes', 'prod_nome', 
                           'prod_doc', 'prod_perc']
        colunas_faltando = [col for col in colunas_esperadas if col not in df.columns]
        
        if colunas_faltando:
            erros.append({
                "linha": 0,
                "campo": "estrutura",
                "valor": f"Colunas faltando: {', '.join(colunas_faltando)}",
                "erro": f"Estrutura do arquivo incorreta. Colunas esperadas nﾃ｣o encontradas. "
                       f"Encoding detectado: {encoding_usado}, Delimitador: {repr(delimitador_usado)}"
            })
        
        df = df.fillna('')  # Substitui NaN por string vazia
        
        total_linhas = len(df)
        linhas_validas = 0
        linhas_com_erro = 0
        
        # Validaﾃｧﾃｵes linha por linha
        for idx, (_, row) in enumerate(df.iterrows()):
            linha_num = idx + 2  # +2 porque linha 1 ﾃｩ header e idx comeﾃｧa em 0
            linha_tem_erro = False
            
            # SEﾃ�グ 1 - IDENTIFICAﾃ�グ
            # ISRC (obrigatﾃｳrio)
            if not row.get('isrc', '').strip():
                erros.append({
                    "linha": linha_num,
                    "campo": "isrc",
                    "valor": "",
                    "erro": "ISRC ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            elif not validar_isrc(row.get('isrc', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "isrc",
                    "valor": row.get('isrc', ''),
                    "erro": "ISRC invﾃ｡lido (deve ter 12 caracteres alfanumﾃｩricos)"
                })
                linha_tem_erro = True
            
            # Tﾃｭtulo (obrigatﾃｳrio)
            if not row.get('titulo', '').strip():
                erros.append({
                    "linha": linha_num,
                    "campo": "titulo",
                    "valor": "",
                    "erro": "Tﾃｭtulo ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            
            # Duraﾃｧﾃ｣o (obrigatﾃｳrio)
            if not row.get('duracao', '').strip():
                erros.append({
                    "linha": linha_num,
                    "campo": "duracao",
                    "valor": "",
                    "erro": "Duraﾃｧﾃ｣o ﾃｩ obrigatﾃｳria"
                })
                linha_tem_erro = True
            elif not validar_duracao(row.get('duracao', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "duracao",
                    "valor": row.get('duracao', ''),
                    "erro": "Duraﾃｧﾃ｣o invﾃ｡lida (formato esperado: mm:ss)"
                })
                linha_tem_erro = True
            
            # Ano lanﾃｧamento (obrigatﾃｳrio)
            if not row.get('ano_lanc', '').strip():
                erros.append({
                    "linha": linha_num,
                    "campo": "ano_lanc",
                    "valor": "",
                    "erro": "Ano de lanﾃｧamento ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            elif not validar_ano(row.get('ano_lanc', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "ano_lanc",
                    "valor": row.get('ano_lanc', ''),
                    "erro": "Ano de lanﾃｧamento invﾃ｡lido"
                })
                linha_tem_erro = True
            
            # Gﾃｪnero (obrigatﾃｳrio)
            if not row.get('genero', '').strip():
                erros.append({
                    "linha": linha_num,
                    "campo": "genero",
                    "valor": "",
                    "erro": "Gﾃｪnero ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            elif not validar_genero(row.get('genero', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "genero",
                    "valor": row.get('genero', ''),
                    "erro": f"Gﾃｪnero invﾃ｡lido (valores vﾃ｡lidos: {', '.join(GENEROS[:5])}...)"
                })
                linha_tem_erro = True
            
            # Versﾃ｣o (opcional, mas valida se preenchido)
            if row.get('versao', '').strip() and not validar_versao(row.get('versao', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "versao",
                    "valor": row.get('versao', ''),
                    "erro": "Versﾃ｣o invﾃ｡lida"
                })
                linha_tem_erro = True
            
            # Idioma (opcional, mas valida se preenchido)
            if row.get('idioma', '').strip() and not validar_idioma(row.get('idioma', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "idioma",
                    "valor": row.get('idioma', ''),
                    "erro": "Idioma invﾃ｡lido"
                })
                linha_tem_erro = True
            
            # Ano gravaﾃｧﾃ｣o (opcional, mas valida se preenchido)
            if row.get('ano_grav', '').strip() and not validar_ano(row.get('ano_grav', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "ano_grav",
                    "valor": row.get('ano_grav', ''),
                    "erro": "Ano de gravaﾃｧﾃ｣o invﾃ｡lido"
                })
                linha_tem_erro = True
            
            # SEﾃ�グ 2 - OBRA MUSICAL
            # Tﾃｭtulo obra (obrigatﾃｳrio)
            if not row.get('titulo_obra', '').strip():
                erros.append({
                    "linha": linha_num,
                    "campo": "titulo_obra",
                    "valor": "",
                    "erro": "Tﾃｭtulo da obra ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            
            # Autores (obrigatﾃｳrio)
            autores = parse_autores(row.get('autores', ''))
            if not autores:
                erros.append({
                    "linha": linha_num,
                    "campo": "autores",
                    "valor": row.get('autores', ''),
                    "erro": "Pelo menos um autor ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            else:
                # Valida cada autor
                for autor in autores:
                    if not autor.get('nome'):
                        erros.append({
                            "linha": linha_num,
                            "campo": "autores",
                            "valor": str(autor),
                            "erro": "Autor sem nome"
                        })
                        linha_tem_erro = True
                    if not validar_cpf(autor.get('cpf', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "autores",
                            "valor": autor.get('cpf', ''),
                            "erro": f"CPF invﾃ｡lido para autor {autor.get('nome', '')}"
                        })
                        linha_tem_erro = True
                    if not validar_funcao_autor(autor.get('funcao', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "autores",
                            "valor": autor.get('funcao', ''),
                            "erro": f"Funﾃｧﾃ｣o invﾃ｡lida para autor {autor.get('nome', '')}"
                        })
                        linha_tem_erro = True
                
                # Valida soma dos percentuais autorais
                percentuais_autores = [a.get('percentual', 0) for a in autores]
                if not validar_percentuais_autorais(percentuais_autores):
                    erros.append({
                        "linha": linha_num,
                        "campo": "autores",
                        "valor": f"Soma: {sum(percentuais_autores)}%",
                        "erro": "Soma dos percentuais autorais deve ser 100%"
                    })
                    linha_tem_erro = True
            
            # Editoras (opcional)
            editoras = parse_editoras(row.get('editoras', ''))
            if editoras:
                for editora in editoras:
                    if not validar_cnpj(editora.get('cnpj', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "editoras",
                            "valor": editora.get('cnpj', ''),
                            "erro": f"CNPJ invﾃ｡lido para editora {editora.get('nome', '')}"
                        })
                        linha_tem_erro = True
                
                percentuais_editoras = [e.get('percentual', 0) for e in editoras]
                if not validar_percentuais_editoras(percentuais_editoras):
                    erros.append({
                        "linha": linha_num,
                        "campo": "editoras",
                        "valor": f"Soma: {sum(percentuais_editoras)}%",
                        "erro": "Soma dos percentuais de editoras deve ser 100%"
                    })
                    linha_tem_erro = True
            
            # SEﾃ�グ 3 - TITULARES CONEXOS
            # Intﾃｩrpretes (obrigatﾃｳrio)
            interpretes = parse_interpretes(row.get('interpretes', ''))
            if not interpretes:
                erros.append({
                    "linha": linha_num,
                    "campo": "interpretes",
                    "valor": "",
                    "erro": "Pelo menos um intﾃｩrprete ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            else:
                for interprete in interpretes:
                    if not validar_cpf(interprete.get('doc', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "interpretes",
                            "valor": interprete.get('doc', ''),
                            "erro": f"CPF invﾃ｡lido para intﾃｩrprete {interprete.get('nome', '')}"
                        })
                        linha_tem_erro = True
                    if not validar_categoria_interprete(interprete.get('categoria', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "interpretes",
                            "valor": interprete.get('categoria', ''),
                            "erro": f"Categoria invﾃ｡lida para intﾃｩrprete {interprete.get('nome', '')}"
                        })
                        linha_tem_erro = True
                    if interprete.get('associacao') and not validar_associacao(interprete.get('associacao', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "interpretes",
                            "valor": interprete.get('associacao', ''),
                            "erro": f"Associaﾃｧﾃ｣o invﾃ｡lida para intﾃｩrprete {interprete.get('nome', '')}"
                        })
                        linha_tem_erro = True
            
            # Mﾃｺsicos (opcional)
            musicos = parse_musicos(row.get('musicos', ''))
            if musicos:
                for musico in musicos:
                    if not validar_cpf(musico.get('cpf', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "musicos",
                            "valor": musico.get('cpf', ''),
                            "erro": f"CPF invﾃ｡lido para mﾃｺsico {musico.get('nome', '')}"
                        })
                        linha_tem_erro = True
                    if not validar_tipo_musico(musico.get('tipo', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "musicos",
                            "valor": musico.get('tipo', ''),
                            "erro": f"Tipo invﾃ｡lido para mﾃｺsico {musico.get('nome', '')}"
                        })
                        linha_tem_erro = True
            
            # Valida soma dos direitos conexos
            perc_interpretes = sum(i.get('percentual', 0) for i in interpretes)
            perc_musicos = sum(m.get('percentual', 0) for m in musicos)
            perc_produtor = 0
            if row.get('prod_perc', '').strip():
                try:
                    perc_produtor = float(str(row.get('prod_perc', '')).replace('%', '').replace(',', '.'))
                except ValueError:
                    pass
            
            if not validar_percentuais_conexos(perc_interpretes, perc_musicos, perc_produtor):
                erros.append({
                    "linha": linha_num,
                    "campo": "percentuais_conexos",
                    "valor": f"Intﾃｩrpretes: {perc_interpretes}%, Mﾃｺsicos: {perc_musicos}%, Produtor: {perc_produtor}%",
                    "erro": "Soma dos direitos conexos (intﾃｩrpretes + mﾃｺsicos + produtor) deve ser 100%"
                })
                linha_tem_erro = True
            
            # SEﾃ�グ 4 - PRODUTOR
            # Nome produtor (obrigatﾃｳrio)
            if not row.get('prod_nome', '').strip():
                erros.append({
                    "linha": linha_num,
                    "campo": "prod_nome",
                    "valor": "",
                    "erro": "Nome do produtor ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            
            # Documento produtor (obrigatﾃｳrio)
            if not row.get('prod_doc', '').strip():
                erros.append({
                    "linha": linha_num,
                    "campo": "prod_doc",
                    "valor": "",
                    "erro": "Documento do produtor ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            else:
                doc_prod = limpar_documento(row.get('prod_doc', ''))
                if len(doc_prod) == 11:
                    if not validar_cpf(doc_prod):
                        erros.append({
                            "linha": linha_num,
                            "campo": "prod_doc",
                            "valor": row.get('prod_doc', ''),
                            "erro": "CPF do produtor invﾃ｡lido"
                        })
                        linha_tem_erro = True
                elif len(doc_prod) == 14:
                    if not validar_cnpj(doc_prod):
                        erros.append({
                            "linha": linha_num,
                            "campo": "prod_doc",
                            "valor": row.get('prod_doc', ''),
                            "erro": "CNPJ do produtor invﾃ｡lido"
                        })
                        linha_tem_erro = True
                else:
                    erros.append({
                        "linha": linha_num,
                        "campo": "prod_doc",
                        "valor": row.get('prod_doc', ''),
                        "erro": "Documento do produtor deve ser CPF (11 dﾃｭgitos) ou CNPJ (14 dﾃｭgitos)"
                    })
                    linha_tem_erro = True
            
            # Percentual produtor (obrigatﾃｳrio)
            if not row.get('prod_perc', '').strip():
                erros.append({
                    "linha": linha_num,
                    "campo": "prod_perc",
                    "valor": "",
                    "erro": "Percentual do produtor ﾃｩ obrigatﾃｳrio"
                })
                linha_tem_erro = True
            
            # Associaﾃｧﾃ｣o produtor (opcional, mas valida se preenchido)
            if row.get('prod_assoc', '').strip() and not validar_associacao(row.get('prod_assoc', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "prod_assoc",
                    "valor": row.get('prod_assoc', ''),
                    "erro": "Associaﾃｧﾃ｣o do produtor invﾃ｡lida"
                })
                linha_tem_erro = True
            
            # Data inﾃｭcio produtor (opcional, mas valida se preenchido)
            if row.get('prod_data_ini', '').strip() and not validar_data(row.get('prod_data_ini', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "prod_data_ini",
                    "valor": row.get('prod_data_ini', ''),
                    "erro": "Data de inﾃｭcio do produtor invﾃ｡lida (formato: dd/mm/yyyy ou yyyy-mm-dd)"
                })
                linha_tem_erro = True
            
            # SEﾃ�グ 5 - LANﾃ②MENTO (validaﾃｧﾃｵes opcionais)
            if row.get('tipo_lanc', '').strip() and not validar_tipo_lancamento(row.get('tipo_lanc', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "tipo_lanc",
                    "valor": row.get('tipo_lanc', ''),
                    "erro": "Tipo de lanﾃｧamento invﾃ｡lido"
                })
                linha_tem_erro = True
            
            if row.get('formato', '').strip() and not validar_formato(row.get('formato', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "formato",
                    "valor": row.get('formato', ''),
                    "erro": "Formato invﾃ｡lido"
                })
                linha_tem_erro = True
            
            if row.get('data_lanc', '').strip() and not validar_data(row.get('data_lanc', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "data_lanc",
                    "valor": row.get('data_lanc', ''),
                    "erro": "Data de lanﾃｧamento invﾃ｡lida (formato: dd/mm/yyyy ou yyyy-mm-dd)"
                })
                linha_tem_erro = True
            
            # SEﾃ�グ 6 - ADMINISTRATIVO
            if row.get('situacao', '').strip() and not validar_situacao(row.get('situacao', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "situacao",
                    "valor": row.get('situacao', ''),
                    "erro": "Situaﾃｧﾃ｣o invﾃ｡lida"
                })
                linha_tem_erro = True
            
            if row.get('data_cad', '').strip() and not validar_data(row.get('data_cad', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "data_cad",
                    "valor": row.get('data_cad', ''),
                    "erro": "Data de cadastro invﾃ｡lida (formato: dd/mm/yyyy ou yyyy-mm-dd)"
                })
                linha_tem_erro = True
            
            # SEﾃ�グ 7 - DOCUMENTOS
            documentos = parse_documentos(row.get('documentos', ''))
            if documentos:
                for doc in documentos:
                    if not validar_tipo_documento(doc.get('tipo', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "documentos",
                            "valor": doc.get('tipo', ''),
                            "erro": f"Tipo de documento invﾃ｡lido: {doc.get('tipo', '')}"
                        })
                        linha_tem_erro = True
                    if doc.get('data') and not validar_data(doc.get('data', '')):
                        erros.append({
                            "linha": linha_num,
                            "campo": "documentos",
                            "valor": doc.get('data', ''),
                            "erro": f"Data invﾃ｡lida no documento {doc.get('tipo', '')}"
                        })
                        linha_tem_erro = True
            
            # SEﾃ�グ 8 - DISTRIBUIﾃ�グ
            if row.get('territorio', '').strip() and not validar_territorio(row.get('territorio', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "territorio",
                    "valor": row.get('territorio', ''),
                    "erro": "Territﾃｳrio invﾃ｡lido"
                })
                linha_tem_erro = True
            
            if row.get('tipos_exec', '').strip() and not validar_tipo_execucao(row.get('tipos_exec', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "tipos_exec",
                    "valor": row.get('tipos_exec', ''),
                    "erro": "Tipo de execuﾃｧﾃ｣o invﾃ｡lido"
                })
                linha_tem_erro = True
            
            if row.get('prioridade', '').strip() and not validar_prioridade(row.get('prioridade', '')):
                erros.append({
                    "linha": linha_num,
                    "campo": "prioridade",
                    "valor": row.get('prioridade', ''),
                    "erro": "Prioridade invﾃ｡lida"
                })
                linha_tem_erro = True
            
            if not linha_tem_erro:
                linhas_validas += 1
            else:
                linhas_com_erro += 1
        
        return df, erros, total_linhas, linhas_validas, linhas_com_erro
        
    except Exception as e:
        erros.append({
            "linha": 0,
            "campo": "arquivo",
            "valor": "",
            "erro": f"Erro ao processar arquivo: {str(e)}"
        })
        return pd.DataFrame(), erros, 0, 0, 0


def processar_arquivo_fonogramas(caminho_arquivo: str) -> Dict:
    
    df, erros_gerais, _, _, _ = processar_csv(caminho_arquivo)
    
    dados = []
    if not df.empty:
        # Converter DataFrame para lista de dicion疵ios
        # fillna('') garante que n縊 haja NaN
        dados = df.fillna('').to_dict(orient='records')
    
    return {
        'dados': dados,
        'erros': erros_gerais
    }

