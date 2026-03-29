from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])

@router.post("/verificar-pin")
async def verificar_pin(pin: str):
    # TODO: Validar PIN contra a base de porteiros para autorizar a operação
    pass