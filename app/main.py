import os
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services import db_crud
from app.core.security import hash_pin
from app.models.schemas import SessionLocal, Porteiro

import secrets
from app.core.config import ADMIN_LOGIN, ADMIN_PASSWORD
# Gerenciador de Sessões em Memória (Volátil)
# Armazena mapeamento: {"token_hex": {"role": "admin|cancela", "id": int, "nome": str}}
SESSIONS = {}

app = FastAPI(title="Sistema de Encomendas OM")

# ==========================================
# 🔐 DEPENDÊNCIAS DE AUTORIZAÇÃO (RBAC)
# ==========================================

def obter_sessao_atual(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente ou inválido")
    
    token = authorization.split(" ")[1]
    sessao = SESSIONS.get(token)
    
    if not sessao:
        raise HTTPException(status_code=401, detail="Sessão expirada ou inválida")
    return sessao

def exigir_admin(sessao: dict = Depends(obter_sessao_atual)):
    if sessao.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado: Requer privilégios de administrador")
    return sessao

def exigir_cancela(sessao: dict = Depends(obter_sessao_atual)):
    if sessao.get("role") not in ["cancela", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado: Requer acesso à cancela")
    return sessao

# ==========================================
# 🧱 MODELOS PYDANTIC (Validação de Dados)
# ==========================================

class EncomendaItem(BaseModel):
    destinatario: str
    descricao: str
    observacoes: Optional[str] = ""
    empresa_transporte: str
    entregador: str

class LoteEntrada(BaseModel):
    encomendas: List[EncomendaItem]
    pin: str

class BaixaEncomenda(BaseModel):
    pin: str
    recebedor_nome: str
    observacao_baixa: Optional[str] = ""

class PorteiroCreate(BaseModel):
    graduacao: str
    nome_guerra: str
    nome_completo: str
    login: str
    pin: str

class PorteiroUpdate(BaseModel):
    graduacao: str
    nome_guerra: str
    nome_completo: str
    login: str
    pin: Optional[str] = None

# Dependência para injetar o DB nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 📡 WEBSOCKETS (Atualização em Tempo Real)
# ==========================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==========================================
# 📦 ROTAS DE ENCOMENDAS (Operação)
# ==========================================

@app.get("/api/encomendas/")
def listar_encomendas(db: Session = Depends(get_db), sessao: dict = Depends(exigir_cancela)):
    return db_crud.get_encomendas_ativas(db)

@app.post("/api/encomendas/lote")
async def registrar_lote_encomendas(lote: LoteEntrada, db: Session = Depends(get_db), sessao: dict = Depends(exigir_cancela)):
    # Nova lógica do Prefixo + PIN
    resultado = db_crud.get_porteiro_by_codigo(db, lote.pin) 
    if not resultado or resultado[0] is None:
        raise HTTPException(status_code=403, detail="Formato de PIN inválido. Use: ID + PIN.")
    
    porteiro, pin_tentativa = resultado
    if porteiro.pin_hash != hash_pin(pin_tentativa):
        raise HTTPException(status_code=403, detail="ID do Porteiro ou PIN inválidos.")
    
    # 2. Converte os dados validados pelo Pydantic para dicionários
    lista_dados = [item.dict() for item in lote.encomendas]
    
    # 3. Salva tudo no banco de dados de uma vez
    novas_encomendas = db_crud.criar_encomendas_lote(db, lista_dados, porteiro.id)
    
    # 4. Avisa a tela da cancela para recarregar
    await manager.broadcast("atualizar")
    return {"message": f"{len(novas_encomendas)} encomendas registradas com sucesso."}

# ROTA DE ENTREGAR A ENCOMENDA (DAR BAIXA)
@app.put("/api/encomendas/{encomenda_id}/baixa")
async def dar_baixa_encomenda(encomenda_id: int, dados: BaixaEncomenda, db: Session = Depends(get_db), sessao: dict = Depends(exigir_cancela)):
    porteiro = db_crud.get_porteiro_by_pin(db, hash_pin(dados.pin))
    
    # Nova lógica do Prefixo + PIN
    resultado = db_crud.get_porteiro_by_codigo(db, dados.pin) 
    if not resultado or resultado[0] is None:
        raise HTTPException(status_code=403, detail="Formato de PIN inválido. Use: ID + PIN.")
    
    porteiro, pin_tentativa = resultado
    if porteiro.pin_hash != hash_pin(pin_tentativa):
        raise HTTPException(status_code=403, detail="ID do Porteiro ou PIN inválidos.")
        
    encomenda = db_crud.dar_baixa_encomenda(db, encomenda_id, porteiro.id, dados.recebedor_nome, dados.observacao_baixa)
    if not encomenda:
        raise HTTPException(status_code=404, detail="Encomenda não encontrada ou já entregue.")
        
    await manager.broadcast("atualizar")
    return {"message": "Baixa realizada com sucesso."}


# MODELO DE DADOS PARA EXCLUSÃO
class CancelarEncomenda(BaseModel):
    pin: str
    motivo: str


# ROTA DE EXCLUIR/CANCELAR A ENCOMENDA
@app.put("/api/encomendas/{encomenda_id}/cancelar")
async def cancelar_encomenda(encomenda_id: int, dados: CancelarEncomenda, db: Session = Depends(get_db), sessao: dict = Depends(exigir_cancela)):
    # Nova lógica do Prefixo + PIN
    resultado = db_crud.get_porteiro_by_codigo(db, dados.pin) 
    if not resultado or resultado[0] is None:
        raise HTTPException(status_code=403, detail="Formato de PIN inválido. Use: ID + PIN.")
    
    porteiro, pin_tentativa = resultado
    if porteiro.pin_hash != hash_pin(pin_tentativa):
        raise HTTPException(status_code=403, detail="ID do Porteiro ou PIN inválidos.")
    
    encomenda = db_crud.cancelar_encomenda(db, encomenda_id, porteiro.id, dados.motivo)
    if not encomenda:
        raise HTTPException(status_code=404, detail="Encomenda não encontrada ou já processada")
    
    await manager.broadcast("atualizar")
    return {"msg": "Registro excluído com sucesso"}

@app.get("/api/historico")
def obter_historico(
    data_inicio: Optional[str] = None, 
    data_fim: Optional[str] = None, 
    status: Optional[str] = None,
    destinatario: Optional[str] = None,
    recebedor_nome: Optional[str] = None,
    porteiro_nome_guerra: Optional[str] = None,
    db: Session = Depends(get_db),
    sessao: dict = Depends(exigir_cancela)
):
    return db_crud.get_historico_completo(
        db, data_inicio, data_fim, status, destinatario, recebedor_nome, porteiro_nome_guerra
    )

class LoginRequest(BaseModel):
    login: str
    senha: str

@app.post("/api/login")
def realizar_login(dados: LoginRequest, db: Session = Depends(get_db)):
    novo_token = secrets.token_hex(32) # Gera um hash aleatório de 64 caracteres
    
    if dados.login == ADMIN_LOGIN and dados.senha == ADMIN_PASSWORD:
        SESSIONS[novo_token] = {"role": "admin", "id": 0, "nome": "Administrador"}
        return {
            "token": novo_token, 
            "role": "admin", 
            "nome": "Administrador"
        }

    # Verifica se é um Porteiro/Cancela válido
    porteiro = db.query(Porteiro).filter(Porteiro.login == dados.login).first()
    
    if porteiro and porteiro.pin_hash == hash_pin(dados.senha):
        SESSIONS[novo_token] = {"role": "cancela", "id": porteiro.id, "nome": porteiro.nome_guerra}
        return {
            "token": novo_token, 
            "role": "cancela", 
            "nome": porteiro.nome_guerra
        }

    raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

# ==========================================
# 🛡️ ROTAS DO ADMIN (Gestão de Porteiros)
# ==========================================

@app.get("/api/porteiros/")
def listar_porteiros(db: Session = Depends(get_db), sessao: dict = Depends(exigir_admin)):
    return db_crud.get_porteiros(db)

@app.post("/api/porteiros/")
def criar_porteiro(dados: PorteiroCreate, db: Session = Depends(get_db), sessao: dict = Depends(exigir_admin)):
    # Chamamos o CRUD passando os dados. A lógica do ID vago fica lá dentro.
    sucesso = db_crud.criar_porteiro(
        db, 
        dados.graduacao, 
        dados.nome_guerra, 
        dados.nome_completo, 
        dados.login, 
        dados.pin
    )
    if not sucesso:
        raise HTTPException(status_code=400, detail="Erro ao criar porteiro ou limite de IDs atingido.")
    return {"message": "Porteiro cadastrado com sucesso!"}

@app.get("/api/porteiros/publico")
def listar_ids_publicos(db: Session = Depends(get_db)):
    # Retorna apenas o necessário para a consulta na cancela
    porteiros = db.query(Porteiro).filter(Porteiro.login != "admin").all()
    return [{"numero_id": p.numero_id, "graduacao": p.graduacao, "nome_guerra": p.nome_guerra} for p in porteiros]

@app.delete("/api/porteiros/{porteiro_id}")
def deletar_porteiro(porteiro_id: int, db: Session = Depends(get_db), sessao: dict = Depends(exigir_admin)):
    porteiro = db_crud.deletar_porteiro(db, porteiro_id)
    if not porteiro:
        raise HTTPException(status_code=404, detail="Porteiro não encontrado.")
    return {"message": "Porteiro removido com sucesso."}

@app.put("/api/porteiros/{porteiro_id}")
def atualizar_porteiro(porteiro_id: int, dados: PorteiroUpdate, db: Session = Depends(get_db), sessao: dict = Depends(exigir_admin)):
    porteiro = db.query(Porteiro).filter(Porteiro.id == porteiro_id).first()
    if not porteiro:
        raise HTTPException(status_code=404, detail="Porteiro não encontrado.")
    
    # Impede que dois militares tenham o mesmo login
    if dados.login != porteiro.login:
        login_existente = db.query(Porteiro).filter(Porteiro.login == dados.login).first()
        if login_existente:
            raise HTTPException(status_code=400, detail="Login já está em uso.")

    # Atualiza os dados
    porteiro.graduacao = dados.graduacao
    porteiro.nome_guerra = dados.nome_guerra
    porteiro.nome_completo = dados.nome_completo
    porteiro.login = dados.login
    
    # Só gera um novo hash se um novo PIN foi digitado no front
    if dados.pin:
        porteiro.pin_hash = hash_pin(dados.pin)
        
    db.commit()
    return {"message": "Porteiro atualizado com sucesso."}

# ==========================================
# 🌐 SERVIDOR DE ARQUIVOS (Frontend)
# ==========================================

# Monta a pasta frontend para servir CSS, JS e HTML secundários
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Rota principal que carrega o index.html da raiz
@app.get("/")
def serve_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"Erro": "Arquivo index.html não encontrado na raiz do projeto."}