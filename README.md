**Arquivo: `README.md`**

Localizar:
```markdown
# 📦 Encomendas OM

Sistema de gerenciamento de encomendas para portarias, projetado com arquitetura modular e atualizações em tempo real via WebSockets.

## 🛠 Tecnologias
* **Backend:** FastAPI, Uvicorn, Python 3.
* **Banco de Dados:** SQLite (via SQLAlchemy).
* **Frontend:** HTML5, CSS3, Vanilla JS.
* **Interface do Servidor (Launcher):** Tkinter, Pystray, Pillow (System Tray).
* **Infraestrutura:** Cron (Linux) para automação de rotinas satélites.
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
Ação: [SUBSTITUIR]
Código:
```markdown
# 📦 Encomendas OM

Sistema robusto de gerenciamento de encomendas para portarias e recepções, projetado com arquitetura modular, atualizações em tempo real via WebSockets e foco em segurança e auditoria (RBAC).

## ✨ Principais Funcionalidades
* **Operação Ágil:** Formulários otimizados com autocompletar dinâmico para transportadoras e descrições.
* **Tempo Real:** Painel de exibição (Cancela) atualizado via WebSockets, sem necessidade de recarregar a página.
* **Histórico e Auditoria:** Registros paginados, filtragem avançada, relatórios para impressão (nativa via navegador com CSS isolado) e exportação de dados brutos (CSV).
* **Segurança:** Controle de acesso baseado em papéis (Admin/Cancela) e senhas criptografadas (SHA-256).
* **Backup Automático:** Rotina isolada para backup diário do banco de dados e geração de relatório em lote.

## 🛠 Tecnologias
* **Backend:** FastAPI, Uvicorn, Python 3.
* **Banco de Dados:** SQLite (via SQLAlchemy).
* **Frontend:** HTML5, CSS3, Vanilla JS.
* **Infraestrutura:** Cron (Linux) para automação de rotinas satélites.

## 🚀 Como Executar

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
3. Inicie a interface gráfica do servidor (Launcher):
   ```bash
   python launcher.py
   ```

### 🔗 Acessos do Sistema
Para acessar o sistema de qualquer computador na mesma rede, utilize o endereço de IP do servidor (Ex: `192.168.1.50`):

* **Menu Principal:** `http://[IP-DO-SERVIDOR]:8000/`
* **Painel da Cancela:** `http://[IP-DO-SERVIDOR]:8000/frontend/cancela.html`
* **Login Operacional:** `http://[IP-DO-SERVIDOR]:8000/frontend/login.html`

*Nota: No computador que hospeda o programa, você ainda pode usar `localhost:8000`.*

### 🔑 Primeiro Acesso (Administrador)
Ao iniciar o servidor pela primeira vez, o sistema injeta automaticamente o usuário administrador padrão no banco de dados.
* **Usuário:** `admin`
* **Senha:** `admin123`

*(Nota: É obrigatório alterar esta senha no Painel Administrativo após o primeiro login).*

### 🗄️ Localização do Banco de Dados (Produção)
Para fins de backup manual, auditoria ou migração, o banco de dados SQLite em ambiente de produção (compilado) é gerado e mantido na pasta segura do usuário logado (padrão FHS/XDG):
`~/.local/share/Encomendas_3RCC/database/`

## 💾 Configuração de Backup Automático (Linux)
O projeto conta com um script satélite (`backup.py`) que roda de forma independente da API principal para garantir a integridade dos dados sem afetar a performance.

Para agendar o backup diário às 23:59, adicione a seguinte linha ao Cron do servidor (`crontab -e`):
```bash
59 23 * * * /usr/bin/python3 /caminho/absoluto/para/o/projeto/backup.py >> /caminho/absoluto/para/o/projeto/backups/cron_log.txt 2>&1
```

## 🏗 Como Compilar (Produção)
Caso deseje gerar um executável binário (Stand-alone):
```bash
python scripts/build_nuitka.py
```
```
Justificativa: Atualiza o README para abranger todas as novas implementações (datalists, paginação, exportações, websockets), corrige os caminhos das rotas (agora o front principal responde no `/` e as páginas dentro de `/frontend/`), documenta o Admin inicial criado pelo novo *seed* do banco e inclui o manual de configuração do script de backup.