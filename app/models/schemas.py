from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from app.core.config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Porteiro(Base):
    __tablename__ = "porteiros"
    id = Column(Integer, primary_key=True, index=True)
    graduacao = Column(String)      # Ex: Sd, Cb, Sgt
    nome_guerra = Column(String)   # Ex: Silva
    nome_completo = Column(String) # Nome civil completo
    login = Column(String, unique=True, index=True)
    pin_hash = Column(String)      # PIN armazenado com segurança

class Encomenda(Base):
    __tablename__ = "encomendas"
    id = Column(Integer, primary_key=True, index=True)
    destinatario = Column(String, index=True)
    descricao = Column(String)
    observacoes = Column(String, nullable=True)  # <-- CAMPO NOVO AQUI
    empresa_transporte = Column(String)          # <-- CAMPO NOVO AQUI
    data_chegada = Column(DateTime, default=datetime.now)
    data_entrega = Column(DateTime, nullable=True)
    status = Column(String, default="Na Portaria")
    recebedor_nome = Column(String, nullable=True)
    observacao_baixa = Column(String, nullable=True) # "Na Portaria" ou "Entregue"

class LogOperacao(Base):
    __tablename__ = "logs_operacoes"
    id = Column(Integer, primary_key=True, index=True)
    encomenda_id = Column(Integer, ForeignKey("encomendas.id"))
    porteiro_id = Column(Integer, ForeignKey("porteiros.id"))
    acao = Column(String) # "ENTRADA" ou "BAIXA"
    data_hora = Column(DateTime, default=datetime.now)

# Cria o arquivo SQLite e as tabelas automaticamente na inicialização
Base.metadata.create_all(bind=engine)