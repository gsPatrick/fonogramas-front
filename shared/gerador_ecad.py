"""
Gerador de arquivos ECAD
Gera arquivos Excel e EXP no formato aceito pelo ECAD
"""

import os
from datetime import datetime
from typing import List, Dict
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from models import Fonograma


def gerar_excel_ecad(fonogramas: List[Fonograma], output_path: str) -> Dict:
    """
    Gera arquivo Excel no formato ECAD
    
    Args:
        fonogramas: Lista de objetos Fonograma
        output_path: Caminho do arquivo de saída
        
    Returns:
        Dict com informações do arquivo gerado
    """
    
    # Preparar dados
    dados = []
    for fono in fonogramas:
        # Extrair autores
        autores_nomes = []
        autores_cpf = []
        autores_funcao = []
        autores_perc = []
        
        for autor in fono.autores_list:
            autores_nomes.append(autor.nome)
            autores_cpf.append(autor.cpf)
            autores_funcao.append(autor.funcao)
            autores_perc.append(str(autor.percentual))
        
        # Extrair intérpretes
        interpretes_nomes = []
        interpretes_doc = []
        interpretes_cat = []
        
        for interp in fono.interpretes_list:
            interpretes_nomes.append(interp.nome)
            interpretes_doc.append(interp.doc)
            interpretes_cat.append(interp.categoria)
        
        # Montar linha
        linha = {
            # Identificação
            'ISRC': fono.isrc,
            'Título do Fonograma': fono.titulo,
            'Versão': fono.versao or '',
            'Duração': fono.duracao,
            'Ano de Gravação': fono.ano_grav or '',
            'Ano de Lançamento': fono.ano_lanc,
            'Idioma': fono.idioma or '',
            'Gênero': fono.genero,
            'Nacional/Internacional': fono.flag_nacional or '',
            'Classificação Trilha': fono.classificacao_trilha or '',
            
            # Obra Musical
            'Título da Obra': fono.titulo_obra,
            'Código da Obra': fono.cod_obra or '',
            'Tipo de Arranjo': fono.tipo_arranjo or '',
            
            # Autores (concatenados com ;)
            'Autores - Nome': ';'.join(autores_nomes),
            'Autores - CPF': ';'.join(autores_cpf),
            'Autores - Função': ';'.join(autores_funcao),
            'Autores - Percentual': ';'.join(autores_perc),
            
            # Intérpretes
            'Intérpretes - Nome': ';'.join(interpretes_nomes),
            'Intérpretes - Documento': ';'.join(interpretes_doc),
            'Intérpretes - Categoria': ';'.join(interpretes_cat),
            
            # Produtor
            'Produtor - Nome': fono.prod_nome,
            'Produtor - Documento': fono.prod_doc,
            'Produtor - Nome Fantasia': fono.prod_fantasia or '',
            'Produtor - Endereço': fono.prod_endereco or '',
            'Produtor - Percentual': fono.prod_perc,
            'Produtor - Associação': fono.prod_assoc or '',
            
            # Lançamento
            'Tipo de Lançamento': fono.tipo_lanc or '',
            'Álbum': fono.album or '',
            'Número da Faixa': fono.faixa or '',
            'Selo': fono.selo or '',
            'Formato': fono.formato or '',
            'País': fono.pais or '',
            'País de Origem': fono.pais_origem or '',
            'Outros Países': fono.paises_adicionais or '',
            'Data de Lançamento': fono.data_lanc or '',
            
            # Administrativo
            'Associação de Gestão': fono.assoc_gestao or '',
            'Território': fono.territorio or '',
            'Tipos de Execução': fono.tipos_exec or '',
        }
        
        dados.append(linha)
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Criar arquivo Excel com formatação por seções
    wb = Workbook()
    ws = wb.active
    ws.title = "Fonogramas ECAD"
    
    # Definir cores por seção (usando cores institucionais SBACEM)
    cores_secao = {
        'identificacao': PatternFill(start_color="22164C", end_color="22164C", fill_type="solid"),  # Roxo
        'obra': PatternFill(start_color="3D2E6B", end_color="3D2E6B", fill_type="solid"),  # Roxo claro
        'autores': PatternFill(start_color="EF234D", end_color="EF234D", fill_type="solid"),  # Vermelho
        'interpretes': PatternFill(start_color="E75A7B", end_color="E75A7B", fill_type="solid"),  # Vermelho claro
        'produtor': PatternFill(start_color="D4A574", end_color="D4A574", fill_type="solid"),  # Bege escuro
        'lancamento': PatternFill(start_color="E1C8B0", end_color="E1C8B0", fill_type="solid"),  # Bege
        'admin': PatternFill(start_color="4A4A4A", end_color="4A4A4A", fill_type="solid"),  # Cinza
    }
    
    # Mapeamento de colunas para seções
    mapa_secao = {
        'ISRC': 'identificacao',
        'Título do Fonograma': 'identificacao',
        'Versão': 'identificacao',
        'Duração': 'identificacao',
        'Ano de Gravação': 'identificacao',
        'Ano de Lançamento': 'identificacao',
        'Idioma': 'identificacao',
        'Gênero': 'identificacao',
        'Nacional/Internacional': 'identificacao',
        'Classificação Trilha': 'identificacao',
        'Título da Obra': 'obra',
        'Código da Obra': 'obra',
        'Tipo de Arranjo': 'obra',
        'Autores - Nome': 'autores',
        'Autores - CPF': 'autores',
        'Autores - Função': 'autores',
        'Autores - Percentual': 'autores',
        'Intérpretes - Nome': 'interpretes',
        'Intérpretes - Documento': 'interpretes',
        'Intérpretes - Categoria': 'interpretes',
        'Produtor - Nome': 'produtor',
        'Produtor - Documento': 'produtor',
        'Produtor - Nome Fantasia': 'produtor',
        'Produtor - Endereço': 'produtor',
        'Produtor - Percentual': 'produtor',
        'Produtor - Associação': 'produtor',
        'Tipo de Lançamento': 'lancamento',
        'Álbum': 'lancamento',
        'Número da Faixa': 'lancamento',
        'Selo': 'lancamento',
        'Formato': 'lancamento',
        'País': 'lancamento',
        'País de Origem': 'lancamento',
        'Outros Países': 'lancamento',
        'Data de Lançamento': 'lancamento',
        'Associação de Gestão': 'admin',
        'Território': 'admin',
        'Tipos de Execução': 'admin',
    }
    
    header_font = Font(bold=True, color="FFFFFF", size=10)
    header_font_dark = Font(bold=True, color="22164C", size=10)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Cores para dados alternados
    row_fill_light = PatternFill(start_color="F8F8F8", end_color="F8F8F8", fill_type="solid")
    row_fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    
    # Escrever cabeçalhos com cores por seção
    for col_idx, col_name in enumerate(df.columns, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        
        # Determinar seção e cor
        secao = mapa_secao.get(col_name, 'admin')
        cell.fill = cores_secao[secao]
        
        # Fonte branca para cores escuras, escura para cores claras
        if secao in ['lancamento']:
            cell.font = header_font_dark
        else:
            cell.font = header_font
        
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)
        cell.border = border
        
        # Ajustar largura da coluna
        if 'Nome' in col_name and 'Fantasia' not in col_name:
            ws.column_dimensions[cell.column_letter].width = 30
        elif 'Título' in col_name:
            ws.column_dimensions[cell.column_letter].width = 25
        elif 'Documento' in col_name or 'CPF' in col_name:
            ws.column_dimensions[cell.column_letter].width = 16
        elif 'ISRC' in col_name:
            ws.column_dimensions[cell.column_letter].width = 14
        elif 'Percentual' in col_name:
            ws.column_dimensions[cell.column_letter].width = 12
        else:
            ws.column_dimensions[cell.column_letter].width = 15
    
    # Escrever dados com cores alternadas
    for row_idx, row_data in enumerate(df.values, 2):
        row_fill = row_fill_light if row_idx % 2 == 0 else row_fill_white
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = border
            cell.fill = row_fill
            cell.alignment = Alignment(vertical='center', wrap_text=False)  # Sem wrap para células compactas
    
    # Congelar primeira linha e primeira coluna (ISRC)
    ws.freeze_panes = 'B2'
    
    # Altura da linha do cabeçalho (compacto)
    ws.row_dimensions[1].height = 25
    
    # Adicionar filtros
    ws.auto_filter.ref = ws.dimensions
    
    # Salvar
    wb.save(output_path)
    
    return {
        'arquivo': output_path,
        'total_fonogramas': len(fonogramas),
        'formato': 'EXCEL',
        'tamanho_bytes': os.path.getsize(output_path) if os.path.exists(output_path) else 0
    }


def gerar_exp_ecad(fonogramas: List[Fonograma], output_path: str) -> Dict:
    """
    Gera arquivo .EXP no formato ECAD
    
    Nota: O formato .EXP é proprietário do ECAD.
    Esta implementação é um placeholder e deve ser ajustada
    conforme especificação técnica oficial do ECAD.
    
    Args:
        fonogramas: Lista de objetos Fonograma
        output_path: Caminho do arquivo de saída
        
    Returns:
        Dict com informações do arquivo gerado
    """
    
    # TODO: Implementar formato .EXP conforme especificação ECAD
    # Por enquanto, gera um arquivo de texto delimitado
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Cabeçalho (exemplo - ajustar conforme spec)
        f.write("ISRC|TITULO|DURACAO|ANO_LANC|GENERO|OBRA|PRODUTOR|PRODUTOR_DOC\n")
        
        for fono in fonogramas:
            linha = f"{fono.isrc}|{fono.titulo}|{fono.duracao}|{fono.ano_lanc}|{fono.genero}|{fono.titulo_obra}|{fono.prod_nome}|{fono.prod_doc}\n"
            f.write(linha)
    
    return {
        'arquivo': output_path,
        'total_fonogramas': len(fonogramas),
        'formato': 'EXP',
        'tamanho_bytes': os.path.getsize(output_path) if os.path.exists(output_path) else 0
    }


def validar_antes_envio(fonogramas: List[Fonograma]) -> Dict:
    """
    Valida se fonogramas estão prontos para envio ao ECAD
    
    Args:
        fonogramas: Lista de objetos Fonograma
        
    Returns:
        Dict com resultado da validação
    """
    
    erros = []
    avisos = []
    validos = []
    
    for fono in fonogramas:
        erros_fono = []
        avisos_fono = []
        
        # Validações obrigatórias
        if not fono.isrc:
            erros_fono.append("ISRC é obrigatório")
        
        if not fono.titulo:
            erros_fono.append("Título é obrigatório")
        
        if not fono.duracao:
            erros_fono.append("Duração é obrigatória")
        
        if not fono.ano_lanc:
            erros_fono.append("Ano de lançamento é obrigatório")
        
        if not fono.genero:
            erros_fono.append("Gênero é obrigatório")
        
        if not fono.titulo_obra:
            erros_fono.append("Título da obra é obrigatório")
        
        if not fono.prod_nome:
            erros_fono.append("Nome do produtor é obrigatório")
        
        if not fono.prod_doc:
            erros_fono.append("Documento do produtor é obrigatório")
        
        # Validações de autores
        if not fono.autores_list or len(fono.autores_list) == 0:
            erros_fono.append("Pelo menos um autor é obrigatório")
        
        # Validações de percentuais
        if fono.autores_list:
            total_autores = sum(a.percentual for a in fono.autores_list)
            if abs(total_autores - 100.0) > 0.01:
                avisos_fono.append(f"Percentual de autores não soma 100% ({total_autores}%)")
        
        # Verificar se já foi enviado
        if fono.status_ecad in ['ENVIADO', 'ACEITO']:
            avisos_fono.append(f"Fonograma já foi enviado (status: {fono.status_ecad})")
        
        # Registrar resultado
        if erros_fono:
            erros.append({
                'fonograma_id': fono.id,
                'isrc': fono.isrc,
                'titulo': fono.titulo,
                'erros': erros_fono,
                'avisos': avisos_fono
            })
        else:
            validos.append(fono.id)
            if avisos_fono:
                avisos.append({
                    'fonograma_id': fono.id,
                    'isrc': fono.isrc,
                    'titulo': fono.titulo,
                    'avisos': avisos_fono
                })
    
    return {
        'total': len(fonogramas),
        'validos': len(validos),
        'com_erro': len(erros),
        'com_aviso': len(avisos),
        'erros': erros,
        'avisos': avisos,
        'ids_validos': validos
    }
