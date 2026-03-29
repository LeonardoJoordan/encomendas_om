import os
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services import db_crud
from app.core.security import hash_pin
from app.models.schemas import SessionLocal

app = FastAPI(title="Sistema de Encomendas OM")

# ==========================================
# 🧱 MODELOS PYDANTIC (Validação de Dados)
# ==========================================

class EncomendaItem(BaseModel):
    destinatario: str
    descricao: str
    observacoes: Optional[str] = ""
    empresa_transporte: str

class LoteEntrada(BaseModel):
    encomendas: List[EncomendaItem]
    pin: str

class BaixaEncomenda(BaseModel):
    pin: str

class PorteiroCreate(BaseModel):
    graduacao: str
    nome_guerra: str
    nome_completo: str
    login: str
    pin: str

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
def listar_encomendas(db: Session = Depends(get_db)):
    return db_crud.get_encomendas_ativas(db)

@app.post("/api/encomendas/lote")
async def registrar_lote_encomendas(lote: LoteEntrada, db: Session = Depends(get_db)):
    # 1. Valida quem está fazendo a operação
    porteiro = db_crud.get_porteiro_by_pin(db, hash_pin(lote.pin))
    if not porteiro:
        raise HTTPException(status_code=403, detail="PIN da Cancela inválido.")
    
    # 2. Converte os dados validados pelo Pydantic para dicionários
    lista_dados = [item.dict() for item in lote.encomendas]
    
    # 3. Salva tudo no banco de dados de uma vez
    novas_encomendas = db_crud.criar_encomendas_lote(db, lista_dados, porteiro.id)
    
    # 4. Avisa a tela da cancela para recarregar
    await manager.broadcast("atualizar")
    return {"message": f"{len(novas_encomendas)} encomendas registradas com sucesso."}

@app.put("/api/encomendas/{encomenda_id}/baixa")
async def dar_baixa(encomenda_id: int, dados: BaixaEncomenda, db: Session = Depends(get_db)):
    porteiro = db_crud.get_porteiro_by_pin(db, hash_pin(dados.pin))
    if not porteiro:
        raise HTTPException(status_code=403, detail="PIN da Cancela inválido.")
        
    encomenda = db_crud.dar_baixa_encomenda(db, encomenda_id, porteiro.id)
    if not encomenda:
        raise HTTPException(status_code=404, detail="Encomenda não encontrada ou já entregue.")
        
    await manager.broadcast("atualizar")
    return {"message": "Baixa realizada com sucesso."}

@app.get("/api/historico")
def obter_historico(
    data_inicio: Optional[str] = None, 
    data_fim: Optional[str] = None, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Converte strings para objetos datetime se necessário aqui
    return db_crud.get_historico_completo(db, data_inicio, data_fim, status)

# ==========================================
# 🛡️ ROTAS DO ADMIN (Gestão de Porteiros)
# ==========================================

@app.get("/api/porteiros/")
def listar_porteiros(db: Session = Depends(get_db)):
    return db_crud.get_porteiros(db)

@app.post("/api/porteiros/")
def criar_porteiro(dados: PorteiroCreate, db: Session = Depends(get_db)):
    return db_crud.criar_porteiro(
        db, dados.graduacao, dados.nome_guerra, dados.nome_completo, dados.login, dados.pin
    )

@app.delete("/api/porteiros/{porteiro_id}")
def deletar_porteiro(porteiro_id: int, db: Session = Depends(get_db)):
    porteiro = db_crud.deletar_porteiro(db, porteiro_id)
    if not porteiro:
        raise HTTPException(status_code=404, detail="Porteiro não encontrado.")
    return {"message": "Porteiro removido com sucesso."}

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