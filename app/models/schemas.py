from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone, timedelta
from app.core.config import DATABASE_URL

BR_TZ = timezone(timedelta(hours=-3))
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def agora_br():
    return datetime.now(BR_TZ)

class Porteiro(Base):
    __tablename__ = "porteiros"
    id = Column(Integer, primary_key=True, index=True)
    numero_id = Column(String(2), unique=True, index=True) # Ex: "01", "02"...
    graduacao = Column(String)      
    nome_guerra = Column(String)   
    nome_completo = Column(String) 
    login = Column(String, unique=True, index=True)
    pin_hash = Column(String)

class Encomenda(Base):
    __tablename__ = "encomendas"
    id = Column(Integer, primary_key=True, index=True)
    destinatario = Column(String, index=True)
    descricao = Column(String)
    observacoes = Column(String, nullable=True)
    empresa_transporte = Column(String)
    entregador = Column(String, nullable=True)
    data_chegada = Column(DateTime, default=agora_br)
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
    data_hora = Column(DateTime, default=agora_br)

# Cria o arquivo SQLite e as tabelas automaticamente na inicialização
Base.metadata.create_all(bind=engine)