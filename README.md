# 📦 Encomendas OM

Sistema de gerenciamento de encomendas para portarias, projetado com arquitetura modular e atualizações em tempo real via WebSockets.

## 🛠 Tecnologias
* **Backend:** FastAPI, Uvicorn, Python 3.
* **Banco de Dados:** SQLite (via SQLAlchemy).
* **Frontend:** HTML5, CSS3, Vanilla JS.
* **Compilação:** Nuitka (gera executável binário independente).

## 🚀 Como Executar em Desenvolvimento

1. Crie um ambiente virtual e ative:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Acesse:
   * **Cancela (Tempo Real):** `http://localhost:8000/cancela.html`
   * **Operação (Porteiro):** `http://localhost:8000/operacao.html`

## 🏗 Como Compilar (Produção)
Execute o script de build para gerar o executável:
```bash
python scripts/build_nuitka.py
```
```
Justificativa: Documentação oficial do repositório, essencial para registrar o escopo, orientar a configuração do ambiente de desenvolvimento e o processo de compilação.