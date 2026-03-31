import os

# Resolve o diretório raiz do projeto (três níveis acima deste arquivo)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Caminho absoluto para o banco de dados na pasta database
DB_PATH = os.path.join(BASE_DIR, "database", "database.sqlite3")
DATABASE_URL = f"sqlite:///{DB_PATH}"
# Credenciais e Segurança (Lê do ambiente ou usa fallback temporário)
ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.getenv("SECRET_KEY", "chave_padrao_insegura_substitua")