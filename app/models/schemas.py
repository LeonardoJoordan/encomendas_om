from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone, timedelta
from app.core.config import DATABASE_URL
import os
import sys

# --- INÍCIO DA VACINA ANTI-ONEFILE DO NUITKA ---
# Detecção "Blindada": Nuitka define variáveis de ambiente que persistem no multiprocessing
is_prod = getattr(sys, 'frozen', False) or "__nuitka_binary_dir" in globals() or os.environ.get('NUITKA_ONEFILE_PARENT')

if is_prod:
    # Caminho absoluto no padrão Linux XDG
    DB_DIR = os.path.expanduser("~/.local/share/Encomendas_3RCC/database")
else:
    # Modo desenvolvimento: Raiz do projeto
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_DIR = os.path.join(BASE_DIR, "database")

# CRÍTICO: Cria a pasta recursivamente se ela não existir
os.makedirs(DB_DIR, exist_ok=True) # Força a criação da pasta no mundo real

# Extrai o nome do arquivo original (ex: "banco.db") da sua URL e cria um caminho absoluto seguro
db_filename = DATABASE_URL.split("/")[-1]
DB_PATH = os.path.join(DB_DIR, db_filename)
ABSOLUTE_DB_URL = f"sqlite:///{DB_PATH}"
# --- FIM DA VACINA ---

BR_TZ = timezone(timedelta(hours=-3))
Base = declarative_base()

# Substituímos a DATABASE_URL pela ABSOLUTE_DB_URL blindada
engine = create_engine(ABSOLUTE_DB_URL, connect_args={"check_same_thread": False})
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