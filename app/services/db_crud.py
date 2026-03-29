from sqlalchemy.orm import Session
from app.models import schemas
from app.core.security import hash_pin
from datetime import datetime

def get_db():
    db = schemas.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 📦 ENCOMENDAS (Operação)
# ==========================================

def get_encomendas_ativas(db: Session):
    # Faz o join com LogOperacao e Porteiro para pegar quem deu entrada
    resultados = db.query(
        schemas.Encomenda,
        schemas.Porteiro.graduacao,
        schemas.Porteiro.nome_guerra
    ).join(
        schemas.LogOperacao, schemas.LogOperacao.encomenda_id == schemas.Encomenda.id
    ).join(
        schemas.Porteiro, schemas.Porteiro.id == schemas.LogOperacao.porteiro_id
    ).filter(
        schemas.Encomenda.status == "Na Portaria",
        schemas.LogOperacao.acao == "ENTRADA"
    ).all()

    # Formata a saída mesclando os dados da Encomenda com os dados do Porteiro
    encomendas_formatadas = []
    for enc, grad, nome in resultados:
        enc_dict = enc.__dict__.copy()
        enc_dict.pop('_sa_instance_state', None) # Remove metadados internos do SQLAlchemy
        enc_dict['porteiro_graduacao'] = grad
        enc_dict['porteiro_nome_guerra'] = nome
        encomendas_formatadas.append(enc_dict)

    return encomendas_formatadas

def criar_encomendas_lote(db: Session, encomendas_lista: list, porteiro_id: int):
    """Recebe uma lista de dicionários com os dados de várias encomendas e salva todas na mesma transação."""
    novas_encomendas = []
    
    for enc_data in encomendas_lista:
        nova_encomenda = schemas.Encomenda(
            destinatario=enc_data['destinatario'],
            descricao=enc_data['descricao'],
            observacoes=enc_data.get('observacoes', ''),
            empresa_transporte=enc_data['empresa_transporte']
        )
        db.add(nova_encomenda)
        db.flush() # Faz o banco gerar o ID da encomenda antes do commit final

        # Cria o log de entrada para esta encomenda específica
        novo_log = schemas.LogOperacao(
            encomenda_id=nova_encomenda.id,
            porteiro_id=porteiro_id,
            acao="ENTRADA"
        )
        db.add(novo_log)
        novas_encomendas.append(nova_encomenda)
        
    db.commit() # Salva tudo de uma vez (Encomendas + Logs)
    return novas_encomendas

def dar_baixa_encomenda(db: Session, encomenda_id: int, porteiro_id: int, recebedor_nome: str = "", observacao_baixa: str = ""):
    encomenda = db.query(schemas.Encomenda).filter(schemas.Encomenda.id == encomenda_id).first()
    if encomenda and encomenda.status == "Na Portaria":
        encomenda.status = "Entregue"
        encomenda.data_entrega = datetime.now()
        encomenda.recebedor_nome = recebedor_nome
        encomenda.observacao_baixa = observacao_baixa
        
        novo_log = schemas.LogOperacao(
            encomenda_id=encomenda.id,
            porteiro_id=porteiro_id,
            acao="BAIXA"
        )
        db.add(novo_log)
        db.commit()
        db.refresh(encomenda)
    return encomenda

# ==========================================
# 🛡️ PORTEIROS (Admin / Autenticação)
# ==========================================

def get_porteiros(db: Session):
    return db.query(schemas.Porteiro).all()

def get_porteiro_by_pin(db: Session, pin: str):
    # Retorna o porteiro que possui este PIN (usado na hora de dar entrada/baixa)
    return db.query(schemas.Porteiro).filter(schemas.Porteiro.pin_hash == pin).first()

def criar_porteiro(db: Session, graduacao: str, nome_guerra: str, nome_completo: str, login: str, pin: str):
    novo_porteiro = schemas.Porteiro(
        graduacao=graduacao,
        nome_guerra=nome_guerra,
        nome_completo=nome_completo,
        login=login,
        pin_hash=hash_pin(pin)
    )
    db.add(novo_porteiro)
    db.commit()
    db.refresh(novo_porteiro)
    return novo_porteiro
    
def deletar_porteiro(db: Session, porteiro_id: int):
    porteiro = db.query(schemas.Porteiro).filter(schemas.Porteiro.id == porteiro_id).first()
    if porteiro:
        db.delete(porteiro)
        db.commit()
    return porteiro

def get_historico_completo(db: Session, data_inicio=None, data_fim=None, status=None, destinatario=None, recebedor_nome=None, porteiro_nome_guerra=None):
    query = db.query(schemas.Encomenda)

    if porteiro_nome_guerra:
        query = query.join(
            schemas.LogOperacao, schemas.LogOperacao.encomenda_id == schemas.Encomenda.id
        ).join(
            schemas.Porteiro, schemas.Porteiro.id == schemas.LogOperacao.porteiro_id
        ).filter(
            schemas.Porteiro.nome_guerra.ilike(f"%{porteiro_nome_guerra}%"),
            schemas.LogOperacao.acao == "ENTRADA"
        )

    if data_inicio:
        query = query.filter(schemas.Encomenda.data_chegada >= data_inicio)
    if data_fim:
        query = query.filter(schemas.Encomenda.data_chegada <= data_fim)
    if status:
        query = query.filter(schemas.Encomenda.status == status)
    if destinatario:
        query = query.filter(schemas.Encomenda.destinatario.ilike(f"%{destinatario}%"))
    if recebedor_nome:
        query = query.filter(schemas.Encomenda.recebedor_nome.ilike(f"%{recebedor_nome}%"))

    return query.order_by(schemas.Encomenda.data_chegada.desc()).all()