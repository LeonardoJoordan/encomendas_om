from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Encomendas_OM", version="1.0.0")

# Permite comunicação via rede local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Os roteadores (APIs e WebSockets) e a montagem do frontend estático 
# serão importados e registrados aqui nos próximos passos.