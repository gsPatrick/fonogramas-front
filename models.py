"""
Modelos de banco de dados para fonogramas
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import List, Dict

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Usuário do sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(20), default='usuario')  # admin, usuario
    ativo = db.Column(db.Boolean, default=True)
    
    # Campos específicos para associados
    associacao = db.Column(db.String(50))  # ABRAMUS, ECAD, etc
    cpf_cnpj = db.Column(db.String(18))
    
    # Campos para recuperação de senha
    reset_token = db.Column(db.String(100), unique=True, nullable=True, index=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Gera um token único para recuperação de senha válido por 1 hora"""
        import secrets
        from datetime import timedelta
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_reset_token(self):
        """Verifica se o token de reset é válido"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        return datetime.utcnow() < self.reset_token_expiry
    
    def clear_reset_token(self):
        """Limpa o token de reset após uso"""
        self.reset_token = None
        self.reset_token_expiry = None
    
    @property
    def is_admin(self):
        return self.role == 'admin'


class Autor(db.Model):
    """Autor de obra musical"""
    __tablename__ = 'autores'
    
    id = db.Column(db.Integer, primary_key=True)
    fonograma_id = db.Column(db.Integer, db.ForeignKey('fonogramas.id', ondelete='CASCADE'), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    funcao = db.Column(db.String(50), nullable=False)  # COMPOSITOR, LETRISTA, etc
    percentual = db.Column(db.Float, nullable=False)
    cae_ipi = db.Column(db.String(20))  # Código IPI/CAE internacional
    data_nascimento = db.Column(db.String(10))  # dd/mm/yyyy
    nacionalidade = db.Column(db.String(50))  # BRASILEIRO, ESTRANGEIRO, etc
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    fonograma = db.relationship('Fonograma', backref=db.backref('autores_list', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'funcao': self.funcao,
            'percentual': self.percentual,
            'cae_ipi': self.cae_ipi,
            'data_nascimento': self.data_nascimento,
            'nacionalidade': self.nacionalidade
        }


class Editora(db.Model):
    """Editora musical"""
    __tablename__ = 'editoras'
    
    id = db.Column(db.Integer, primary_key=True)
    fonograma_id = db.Column(db.Integer, db.ForeignKey('fonogramas.id', ondelete='CASCADE'), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False)
    percentual = db.Column(db.Float, nullable=False)
    nacionalidade = db.Column(db.String(50))  # BRASILEIRA, ESTRANGEIRA
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    fonograma = db.relationship('Fonograma', backref=db.backref('editoras_list', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'percentual': self.percentual,
            'nacionalidade': self.nacionalidade
        }


class Interprete(db.Model):
    """Intérprete do fonograma"""
    __tablename__ = 'interpretes'
    
    id = db.Column(db.Integer, primary_key=True)
    fonograma_id = db.Column(db.Integer, db.ForeignKey('fonogramas.id', ondelete='CASCADE'), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    doc = db.Column(db.String(14), nullable=False)  # CPF ou CNPJ
    categoria = db.Column(db.String(50), nullable=False)  # PRINCIPAL, COADJUVANTE, etc
    percentual = db.Column(db.Float, nullable=False)
    associacao = db.Column(db.String(50))
    cae_ipi = db.Column(db.String(20))  # Código IPI/CAE internacional
    data_nascimento = db.Column(db.String(10))  # dd/mm/yyyy
    nacionalidade = db.Column(db.String(50))  # BRASILEIRO, ESTRANGEIRO, etc
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    fonograma = db.relationship('Fonograma', backref=db.backref('interpretes_list', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'doc': self.doc,
            'categoria': self.categoria,
            'percentual': self.percentual,
            'associacao': self.associacao,
            'cae_ipi': self.cae_ipi,
            'data_nascimento': self.data_nascimento,
            'nacionalidade': self.nacionalidade
        }


class Musico(db.Model):
    """Músico do fonograma"""
    __tablename__ = 'musicos'
    
    id = db.Column(db.Integer, primary_key=True)
    fonograma_id = db.Column(db.Integer, db.ForeignKey('fonogramas.id', ondelete='CASCADE'), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    instrumento = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # FIXO, EVENTUAL
    percentual = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    fonograma = db.relationship('Fonograma', backref=db.backref('musicos_list', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'instrumento': self.instrumento,
            'tipo': self.tipo,
            'percentual': self.percentual
        }


class Documento(db.Model):
    """Documento relacionado ao fonograma"""
    __tablename__ = 'documentos'
    
    id = db.Column(db.Integer, primary_key=True)
    fonograma_id = db.Column(db.Integer, db.ForeignKey('fonogramas.id', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    referencia = db.Column(db.String(200))
    data = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    fonograma = db.relationship('Fonograma', backref=db.backref('documentos_list', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'referencia': self.referencia,
            'data': self.data
        }


class Fonograma(db.Model):
    """Fonograma principal"""
    __tablename__ = 'fonogramas'
    __table_args__ = (
        db.Index('idx_fonograma_genero_status', 'genero', 'status_ecad'),
        db.Index('idx_fonograma_prod_nome', 'prod_nome'),
        db.Index('idx_fonograma_titulo', 'titulo'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # SEÇÃO 1 - IDENTIFICAÇÃO
    isrc = db.Column(db.String(12), unique=True, nullable=False, index=True)
    titulo = db.Column(db.String(500), nullable=False)
    versao = db.Column(db.String(50))
    duracao = db.Column(db.String(10), nullable=False)  # mm:ss
    ano_grav = db.Column(db.Integer)
    ano_lanc = db.Column(db.Integer, nullable=True)  # Alterado para nullable para evitar erros
    idioma = db.Column(db.String(10))
    genero = db.Column(db.String(50), nullable=False)
    cod_interno = db.Column(db.String(100))
    
    # SEÇÃO 2 - OBRA MUSICAL
    titulo_obra = db.Column(db.String(500), nullable=False)
    cod_obra = db.Column(db.String(100))
    
    # NOVOS CAMPOS (Solicitação)
    pais_origem = db.Column(db.String(100))
    paises_adicionais = db.Column(db.Text)  # Lista de outros países
    flag_nacional = db.Column(db.String(20))  # NACIONAL, INTERNACIONAL
    classificacao_trilha = db.Column(db.String(50))
    tipo_arranjo = db.Column(db.String(20))  # ORIGINAL, ARRANJO
    subdivisao_estrangeiro = db.Column(db.String(50))  # Subdivisão para fonogramas estrangeiros
    publicacao_simultanea = db.Column(db.Boolean, default=False)  # Publicação simultânea
    
    # SEÇÃO 3 - TITULARES CONEXOS (relacionamentos separados)
    
    # SEÇÃO 4 - PRODUTOR
    prod_nome = db.Column(db.String(200), nullable=False)
    prod_doc = db.Column(db.String(14), nullable=False)  # CPF ou CNPJ
    prod_fantasia = db.Column(db.String(200))
    prod_endereco = db.Column(db.String(500))
    prod_perc = db.Column(db.Float, nullable=False)
    prod_assoc = db.Column(db.String(50))
    prod_data_ini = db.Column(db.String(20))
    
    # SEÇÃO 5 - LANÇAMENTO
    tipo_lanc = db.Column(db.String(50))
    album = db.Column(db.String(200))
    faixa = db.Column(db.Integer)
    selo = db.Column(db.String(200))
    formato = db.Column(db.String(20))
    pais = db.Column(db.String(100))
    data_lanc = db.Column(db.String(20))
    
    # SEÇÃO 6 - ADMINISTRATIVO
    assoc_gestao = db.Column(db.String(50))
    data_cad = db.Column(db.String(20))
    situacao = db.Column(db.String(50), default='ATIVO')
    obs_juridicas = db.Column(db.Text)
    historico = db.Column(db.Text)
    
    # SEÇÃO 7 - DOCUMENTOS (relacionamento separado)
    
    # SEÇÃO 8 - DISTRIBUIÇÃO
    territorio = db.Column(db.String(50))
    tipos_exec = db.Column(db.String(50))
    prioridade = db.Column(db.String(20))
    cod_ecad = db.Column(db.String(100))
    
    # SEÇÃO 9 - CONTROLE ECAD
    status_ecad = db.Column(db.String(50), default='NAO_ENVIADO', index=True)
    # Valores: NAO_ENVIADO, SELECIONADO, ENVIADO, ACEITO, RECUSADO, AJUSTADO, REENVIADO
    data_ultimo_envio = db.Column(db.DateTime)
    tentativas_envio = db.Column(db.Integer, default=0)
    ultimo_protocolo_ecad = db.Column(db.String(100))
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_relations=True):
        """Converte fonograma para dicionário"""
        data = {
            'id': self.id,
            'isrc': self.isrc,
            'titulo': self.titulo,
            'versao': self.versao,
            'duracao': self.duracao,
            'ano_grav': self.ano_grav,
            'ano_lanc': self.ano_lanc,
            'idioma': self.idioma,
            'genero': self.genero,
            'cod_interno': self.cod_interno,
            'titulo_obra': self.titulo_obra,
            'cod_obra': self.cod_obra,
            'pais_origem': self.pais_origem,
            'paises_adicionais': self.paises_adicionais,
            'flag_nacional': self.flag_nacional,
            'classificacao_trilha': self.classificacao_trilha,
            'tipo_arranjo': self.tipo_arranjo,
            'subdivisao_estrangeiro': self.subdivisao_estrangeiro,
            'publicacao_simultanea': self.publicacao_simultanea,
            'prod_nome': self.prod_nome,
            'prod_doc': self.prod_doc,
            'prod_fantasia': self.prod_fantasia,
            'prod_endereco': self.prod_endereco,
            'prod_perc': self.prod_perc,
            'prod_assoc': self.prod_assoc,
            'prod_data_ini': self.prod_data_ini,
            'tipo_lanc': self.tipo_lanc,
            'album': self.album,
            'faixa': self.faixa,
            'selo': self.selo,
            'formato': self.formato,
            'pais': self.pais,
            'data_lanc': self.data_lanc,
            'assoc_gestao': self.assoc_gestao,
            'data_cad': self.data_cad,
            'situacao': self.situacao,
            'obs_juridicas': self.obs_juridicas,
            'historico': self.historico,
            'territorio': self.territorio,
            'tipos_exec': self.tipos_exec,
            'prioridade': self.prioridade,
            'cod_ecad': self.cod_ecad,
            # Campos ECAD
            'status_ecad': self.status_ecad,
            'data_ultimo_envio': self.data_ultimo_envio.isoformat() if self.data_ultimo_envio else None,
            'tentativas_envio': self.tentativas_envio,
            'ultimo_protocolo_ecad': self.ultimo_protocolo_ecad,
            # Metadados
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            data['autores'] = [a.to_dict() for a in self.autores_list]
            data['editoras'] = [e.to_dict() for e in self.editoras_list]
            data['interpretes'] = [i.to_dict() for i in self.interpretes_list]
            data['musicos'] = [m.to_dict() for m in self.musicos_list]
            data['documentos'] = [d.to_dict() for d in self.documentos_list]
        
        return data


# Tabela associativa para relacionamento many-to-many entre Fonograma e EnvioECAD
fonograma_envio = db.Table('fonograma_envio',
    db.Column('fonograma_id', db.Integer, db.ForeignKey('fonogramas.id', ondelete='CASCADE'), primary_key=True),
    db.Column('envio_id', db.Integer, db.ForeignKey('envio_ecad.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class EnvioECAD(db.Model):
    """Registro de envio ao ECAD"""
    __tablename__ = 'envio_ecad'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    protocolo = db.Column(db.String(100), unique=True, index=True)  # Protocolo ECAD
    data_envio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    tipo_envio = db.Column(db.String(20), nullable=False)  # TOTAL, PARCIAL
    metodo = db.Column(db.String(20), default='MANUAL')  # MANUAL, API
    formato_arquivo = db.Column(db.String(10))  # EXCEL, EXP
    arquivo_gerado = db.Column(db.String(500))  # Path do arquivo gerado
    total_fonogramas = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='AGUARDANDO_RETORNO')  # AGUARDANDO_RETORNO, PROCESSADO, ERRO
    observacoes = db.Column(db.Text)
    created_by = db.Column(db.String(100))  # Usuário que criou (futuro)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    fonogramas = db.relationship('Fonograma', secondary=fonograma_envio, backref=db.backref('envios', lazy='dynamic'))
    retornos = db.relationship('RetornoECAD', backref='envio', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_fonogramas=False):
        """Converte envio para dicionário"""
        data = {
            'id': self.id,
            'protocolo': self.protocolo,
            'data_envio': self.data_envio.isoformat() if self.data_envio else None,
            'tipo_envio': self.tipo_envio,
            'metodo': self.metodo,
            'formato_arquivo': self.formato_arquivo,
            'arquivo_gerado': self.arquivo_gerado,
            'total_fonogramas': self.total_fonogramas,
            'status': self.status,
            'observacoes': self.observacoes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_fonogramas:
            data['fonogramas'] = [{'id': f.id, 'isrc': f.isrc, 'titulo': f.titulo} for f in self.fonogramas]
        
        return data


class RetornoECAD(db.Model):
    """Registro de retorno do ECAD para cada fonograma"""
    __tablename__ = 'retorno_ecad'
    
    id = db.Column(db.Integer, primary_key=True)
    envio_id = db.Column(db.Integer, db.ForeignKey('envio_ecad.id', ondelete='CASCADE'), nullable=False, index=True)
    fonograma_id = db.Column(db.Integer, db.ForeignKey('fonogramas.id', ondelete='CASCADE'), nullable=False, index=True)
    data_retorno = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status_ecad = db.Column(db.String(50), nullable=False)  # ACEITO, RECUSADO
    codigo_erro = db.Column(db.String(50))  # Código de erro retornado pelo ECAD
    mensagem_erro = db.Column(db.Text)  # Mensagem de erro detalhada
    cod_ecad_gerado = db.Column(db.String(100))  # Código gerado pelo ECAD se aceito
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    fonograma = db.relationship('Fonograma', backref=db.backref('retornos_ecad', lazy=True, cascade='all, delete-orphan'))
    
    def to_dict(self):
        """Converte retorno para dicionário"""
        return {
            'id': self.id,
            'envio_id': self.envio_id,
            'fonograma_id': self.fonograma_id,
            'data_retorno': self.data_retorno.isoformat() if self.data_retorno else None,
            'status_ecad': self.status_ecad,
            'codigo_erro': self.codigo_erro,
            'mensagem_erro': self.mensagem_erro,
            'cod_ecad_gerado': self.cod_ecad_gerado,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class HistoricoFonograma(db.Model):
    """Histórico de alterações do fonograma para auditoria"""
    __tablename__ = 'historico_fonograma'
    
    id = db.Column(db.Integer, primary_key=True)
    fonograma_id = db.Column(db.Integer, db.ForeignKey('fonogramas.id', ondelete='CASCADE'), nullable=False, index=True)
    data_alteracao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    tipo_alteracao = db.Column(db.String(50), nullable=False)  # CRIACAO, EDICAO, ENVIO, RETORNO, REENVIO
    campo_alterado = db.Column(db.String(100))
    valor_anterior = db.Column(db.Text)
    valor_novo = db.Column(db.Text)
    usuario = db.Column(db.String(100))  # Usuário que fez a alteração (futuro)
    motivo = db.Column(db.String(200))
    detalhes = db.Column(db.Text)  # JSON com detalhes adicionais
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com cascade delete
    fonograma = db.relationship('Fonograma', backref=db.backref('historico_alteracoes', lazy=True, cascade='all, delete-orphan', order_by='HistoricoFonograma.data_alteracao.desc()'))
    
    def to_dict(self):
        """Converte histórico para dicionário"""
        return {
            'id': self.id,
            'fonograma_id': self.fonograma_id,
            'data_alteracao': self.data_alteracao.isoformat() if self.data_alteracao else None,
            'tipo_alteracao': self.tipo_alteracao,
            'campo_alterado': self.campo_alterado,
            'valor_anterior': self.valor_anterior,
            'valor_novo': self.valor_novo,
            'usuario': self.usuario,
            'motivo': self.motivo,
            'detalhes': self.detalhes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

