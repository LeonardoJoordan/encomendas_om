from fastapi import APIRouter

router = APIRouter(prefix="/api/encomendas", tags=["Encomendas"])

@router.get("/")
async def listar_encomendas():
    # TODO: Integrar com services/db_crud.py para buscar encomendas ativas
    pass

@router.post("/entrada")
async def registrar_entrada():
    # TODO: Receber dados da encomenda e validar PIN do porteiro
    pass

@router.put("/{encomenda_id}/baixa")
async def registrar_baixa(encomenda_id: int):
    # TODO: Atualizar status para entregue e registrar log
    pass