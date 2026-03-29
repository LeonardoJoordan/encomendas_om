from sqlalchemy.orm import Session
from app.models import schemas
from datetime import datetime

def get_db():
    db = schemas.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_encomendas_ativas(db: Session):
    return db.query(schemas.Encomenda).filter(schemas.Encomenda.status == "Na Portaria").all()

def criar_encomenda(db: Session, destinatario: str, descricao: str, porteiro_id: int):
    nova_encomenda = schemas.Encomenda(destinatario=destinatario, descricao=descricao)
    db.add(nova_encomenda)
    db.commit()
    db.refresh(nova_encomenda)

    novo_log = schemas.LogOperacao(
        encomenda_id=nova_encomenda.id,
        porteiro_id=porteiro_id,
        acao="ENTRADA"
    )
    db.add(novo_log)
    db.commit()
    return nova_encomenda

def dar_baixa_encomenda(db: Session, encomenda_id: int, porteiro_id: int):
    encomenda = db.query(schemas.Encomenda).filter(schemas.Encomenda.id == encomenda_id).first()
    if encomenda and encomenda.status == "Na Portaria":
        encomenda.status = "Entregue"
        encomenda.data_entrega = datetime.now()
        
        novo_log = schemas.LogOperacao(
            encomenda_id=encomenda.id,
            porteiro_id=porteiro_id,
            acao="BAIXA"
        )
        db.add(novo_log)
        db.commit()
    return encomenda