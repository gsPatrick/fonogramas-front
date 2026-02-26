"""
Módulo de validação de dados para fonogramas ECAD/ABRAMUS
"""

import re
from datetime import datetime


# Constantes de valores válidos
VERSOES = ['original', 'remix', 'ao_vivo', 'instrumental', 'edit', 'acoustic', 'radio_edit', 'acapella', 'cover']
IDIOMAS = ['PT', 'EN', 'ES', 'FR', 'IT', 'DE', 'JP', 'KR', 'RU', 'AR']
GENEROS = ['Sertanejo', 'Pop', 'Rock', 'MPB', 'Funk', 'Pagode', 'Forró', 'Axé', 'Gospel', 'Eletrônica', 'Hip-Hop', 'Jazz', 'Blues', 'Country', 'Clássico', 'Reggae', 'Bossa Nova']
FUNCOES_AUTOR = ['COMPOSITOR', 'LETRISTA', 'COMPOSITOR_LETRISTA', 'VERSIONISTA', 'ADAPTADOR']
CATEGORIAS_INTERPRETE = ['PRINCIPAL', 'COADJUVANTE', 'PARTICIPACAO_ESPECIAL']
TIPOS_MUSICO = ['FIXO', 'EVENTUAL']
ASSOCIACOES = ['ABRAMUS', 'UBC', 'AMAR', 'SBACEM', 'SICAM', 'SOCINPRO', 'ASSIM', 'SADEMBRA', 'ANACIM']
TIPOS_LANCAMENTO = ['ALBUM', 'SINGLE', 'EP', 'COMPILACAO', 'TRILHA_SONORA']
FORMATOS = ['DIGITAL', 'FISICO', 'AMBOS']
SITUACOES = ['ATIVO', 'PENDENTE', 'EM_DISPUTA', 'INATIVO']
TERRITORIOS = ['BRASIL', 'INTERNACIONAL', 'AMBOS', 'AMERICA_LATINA', 'EUROPA']
TIPOS_EXECUCAO = ['RADIO', 'TV', 'STREAMING', 'SHOWS', 'SONORIZACAO', 'CINEMA', 'TODOS']
PRIORIDADES = ['NORMAL', 'ALTA', 'URGENTE']
TIPOS_DOCUMENTO = ['DECLARACAO', 'CONTRATO_CESSAO', 'AUTORIZACAO_NOME', 'CONTRATO_INTERPRETE', 'COMPROVANTE_ISRC', 'OUTRO']


def limpar_documento(doc: str) -> str:
    """Remove caracteres não numéricos de CPF/CNPJ"""
    if not doc:
        return ""
    return re.sub(r'\D', '', str(doc))


def validar_cpf(cpf: str) -> bool:
    """Valida CPF (11 dígitos, algoritmo oficial)"""
    if not cpf:
        return False
    
    cpf_limpo = limpar_documento(cpf)
    
    if len(cpf_limpo) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf_limpo == cpf_limpo[0] * 11:
        return False
    
    # Validação dos dígitos verificadores
    def calcular_digito(cpf_base, multiplicadores):
        soma = sum(int(cpf_base[i]) * multiplicadores[i] for i in range(len(multiplicadores)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Primeiro dígito verificador
    mult1 = list(range(10, 1, -1))
    digito1 = calcular_digito(cpf_limpo[:9], mult1)
    
    if int(cpf_limpo[9]) != digito1:
        return False
    
    # Segundo dígito verificador
    mult2 = list(range(11, 1, -1))
    digito2 = calcular_digito(cpf_limpo[:10], mult2)
    
    if int(cpf_limpo[10]) != digito2:
        return False
    
    return True


def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ (14 dígitos, algoritmo oficial)"""
    if not cnpj:
        return False
    
    cnpj_limpo = limpar_documento(cnpj)
    
    if len(cnpj_limpo) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj_limpo == cnpj_limpo[0] * 14:
        return False
    
    # Validação dos dígitos verificadores
    def calcular_digito(cnpj_base, multiplicadores):
        soma = sum(int(cnpj_base[i]) * multiplicadores[i] for i in range(len(multiplicadores)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Primeiro dígito verificador
    mult1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito1 = calcular_digito(cnpj_limpo[:12], mult1)
    
    if int(cnpj_limpo[12]) != digito1:
        return False
    
    # Segundo dígito verificador
    mult2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito2 = calcular_digito(cnpj_limpo[:13], mult2)
    
    if int(cnpj_limpo[13]) != digito2:
        return False
    
    return True


def validar_isrc(isrc: str) -> bool:
    """Valida ISRC - formato: BRUM71601234 (12 caracteres alfanuméricos)"""
    if not isrc:
        return False
    
    isrc_limpo = str(isrc).strip().upper()
    
    # ISRC deve ter exatamente 12 caracteres alfanuméricos
    if len(isrc_limpo) != 12:
        return False
    
    # Deve ser alfanumérico
    if not isrc_limpo.isalnum():
        return False
    
    # Formato padrão: 2 letras (país) + 3 alfanuméricos (registrante) + 7 alfanuméricos (código)
    # Validação básica: apenas verifica se tem 12 caracteres alfanuméricos
    return True


def validar_duracao(duracao: str) -> bool:
    """Valida duração no formato mm:ss"""
    if not duracao:
        return False
    
    duracao = str(duracao).strip()
    
    # Padrão mm:ss
    padrao = r'^(\d{1,2}):([0-5]\d)$'
    match = re.match(padrao, duracao)
    
    if not match:
        return False
    
    minutos = int(match.group(1))
    segundos = int(match.group(2))
    
    # Minutos deve ser >= 0 e < 60 (ou mais se necessário)
    if minutos < 0:
        return False
    
    return True


def validar_percentuais_conexos(interpretes_perc: float, musicos_perc: float, produtor_perc: float) -> bool:
    """Valida se soma dos direitos conexos = 100%"""
    soma = (interpretes_perc or 0) + (musicos_perc or 0) + (produtor_perc or 0)
    return abs(soma - 100.0) < 0.01  # Tolerância para arredondamento


def validar_percentuais_autorais(autores_perc: list[float]) -> bool:
    """Valida se soma dos percentuais autorais = 100%"""
    if not autores_perc:
        return False
    
    soma = sum(p or 0 for p in autores_perc)
    return abs(soma - 100.0) < 0.01  # Tolerância para arredondamento


def validar_percentuais_editoras(editoras_perc: list[float]) -> bool:
    """Valida se soma dos percentuais de editoras = 100%"""
    if not editoras_perc:
        return True  # Editoras são opcionais
    
    soma = sum(p or 0 for p in editoras_perc)
    return abs(soma - 100.0) < 0.01  # Tolerância para arredondamento


def validar_versao(versao: str) -> bool:
    """Valida se versão está na lista de valores válidos"""
    if not versao:
        return True  # Opcional
    return versao.lower() in [v.lower() for v in VERSOES]


def validar_idioma(idioma: str) -> bool:
    """Valida se idioma está na lista de valores válidos"""
    if not idioma:
        return True  # Opcional
    return str(idioma).upper() in IDIOMAS


def validar_genero(genero: str) -> bool:
    """Valida se gênero está na lista de valores válidos"""
    if not genero:
        return False  # Obrigatório
    return str(genero) in GENEROS


def validar_funcao_autor(funcao: str) -> bool:
    """Valida se função do autor está na lista de valores válidos"""
    if not funcao:
        return False
    return str(funcao).upper() in FUNCOES_AUTOR


def validar_categoria_interprete(categoria: str) -> bool:
    """Valida se categoria do intérprete está na lista de valores válidos"""
    if not categoria:
        return False
    return str(categoria).upper() in CATEGORIAS_INTERPRETE


def validar_tipo_musico(tipo: str) -> bool:
    """Valida se tipo de músico está na lista de valores válidos"""
    if not tipo:
        return False
    return str(tipo).upper() in TIPOS_MUSICO


def validar_associacao(assoc: str) -> bool:
    """Valida se associação está na lista de valores válidos"""
    if not assoc:
        return True  # Opcional
    return str(assoc).upper() in ASSOCIACOES


def validar_tipo_lancamento(tipo: str) -> bool:
    """Valida se tipo de lançamento está na lista de valores válidos"""
    if not tipo:
        return True  # Opcional
    return str(tipo).upper() in TIPOS_LANCAMENTO


def validar_formato(formato: str) -> bool:
    """Valida se formato está na lista de valores válidos"""
    if not formato:
        return True  # Opcional
    return str(formato).upper() in FORMATOS


def validar_situacao(situacao: str) -> bool:
    """Valida se situação está na lista de valores válidos"""
    if not situacao:
        return True  # Opcional
    return str(situacao).upper() in SITUACOES


def validar_territorio(territorio: str) -> bool:
    """Valida se território está na lista de valores válidos"""
    if not territorio:
        return True  # Opcional
    return str(territorio).upper() in TERRITORIOS


def validar_tipo_execucao(tipo: str) -> bool:
    """Valida se tipo de execução está na lista de valores válidos"""
    if not tipo:
        return True  # Opcional
    return str(tipo).upper() in TIPOS_EXECUCAO


def validar_prioridade(prioridade: str) -> bool:
    """Valida se prioridade está na lista de valores válidos"""
    if not prioridade:
        return True  # Opcional
    return str(prioridade).upper() in PRIORIDADES


def validar_tipo_documento(tipo: str) -> bool:
    """Valida se tipo de documento está na lista de valores válidos"""
    if not tipo:
        return False
    return str(tipo).upper() in TIPOS_DOCUMENTO


def validar_ano(ano: str) -> bool:
    """Valida se ano é um número válido (1900-2100)"""
    if not ano:
        return True  # Opcional
    
    try:
        ano_int = int(str(ano))
        return 1900 <= ano_int <= 2100
    except ValueError:
        return False


def validar_data(data: str) -> bool:
    """Valida formato de data (dd/mm/yyyy ou yyyy-mm-dd) e se é uma data real"""
    if not data:
        return True  # Opcional
    
    data = str(data).strip()
    
    # Tentar formato dd/mm/yyyy
    try:
        if re.match(r'^\d{2}/\d{2}/\d{4}$', data):
            datetime.strptime(data, '%d/%m/%Y')
            return True
    except ValueError:
        pass
        
    # Tentar formato yyyy-mm-dd
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', data):
            datetime.strptime(data, '%Y-%m-%d')
            return True
    except ValueError:
        pass
    
    return False

def aplicar_regra_varsovia(pais_origem: str, pais_executor: str = 'BRASIL') -> bool:
    """
    Aplica a Regra de Varsóvia para reciprocidade de direitos autorais entre países.
    Conforme manual do ECAD, verifica se o país de origem tem acordo de reciprocidade.
    """
    # Lista detalhada de países signatários e com reciprocidade (Varsóvia/Roma/Berna)
    PAISES_RECIPROCIDADE = [
        'BRASIL', 'ESTADOS UNIDOS', 'REINO UNIDO', 'FRANÇA', 'ALEMANHA', 
        'ITÁLIA', 'ESPANHA', 'PORTUGAL', 'ARGENTINA', 'URUGUAI', 'CHILE', 
        'MÉXICO', 'CANADÁ', 'JAPÃO', 'COREIA DO SUL', 'AUSTRÁLIA', 'ÁUSTRIA',
        'BÉLGICA', 'SUIÇA', 'HOLANDA', 'SUÉCIA', 'NORUEGA', 'DINAMARCA'
    ]
    
    origem = str(pais_origem or '').upper().strip()
    if not origem or origem == 'BRASIL':
        return True
        
    return origem in PAISES_RECIPROCIDADE

def validar_repertorio_internacional(fono) -> bool:
    """Valida conformidade internacional baseada na reciprocidade."""
    if (fono.flag_nacional or '').upper() == 'INTERNACIONAL':
        return aplicar_regra_varsovia(fono.pais_origem)
    return True
