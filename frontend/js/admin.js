<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel do Administrador - Gestão</title>
    <link rel="stylesheet" href="/frontend/css/styles.css">
</head>
<body>
    <header>
        <h1>⚙️ Painel do Administrador</h1>
        <p>Gestão de Efetivo e Histórico Global</p>
    </header>
    
    <main>
        <nav class="tabs">
            <button class="tab-btn active" onclick="switchTab('gerenciar-efetivo')">Gerenciar Efetivo</button>
            <button class="tab-btn" onclick="switchTab('historico-tab')">Histórico Global</button>
        </nav>

        <div id="gerenciar-efetivo" class="tab-content active">
            <section id="gerenciar-porteiro">
                <h2>Cadastrar / Editar Porteiro</h2>
                <form id="form-admin">
                    <input type="hidden" id="porteiro-id">
                    <input type="text" id="porteiro-graduacao" placeholder="Graduação (ex: Sd, Cb, Sgt)" required>
                    <input type="text" id="porteiro-nome-guerra" placeholder="Nome de Guerra" required>
                    <input type="text" id="porteiro-nome" placeholder="Nome Completo" required>
                    <input type="text" id="porteiro-login" placeholder="Login de Acesso" required>
                    <input type="text" id="porteiro-pin" placeholder="PIN da Cancela" required>
                    <button type="submit" id="btn-salvar">Salvar Porteiro</button>
                    <button type="button" id="btn-cancelar" style="display: none; background-color: #dc3545;" onclick="cancelarEdicao()">Cancelar</button>
                </form>
            </section>

            <hr>

            <section id="lista-efetivo">
                <h2>Efetivo Cadastrado</h2>
                <table id="tabela-porteiros" style="table-layout: fixed; width: 100%;">
                    <colgroup>
                        <col style="width: 5%;"> <col style="width: 10%;"> <col style="width: 15%;"> <col style="width: 30%;"> <col style="width: 15%;"> <col style="width: 10%;"> <col style="width: 15%;">
                    </colgroup>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Grad</th>
                            <th>Guerra</th>
                            <th>Nome Completo</th>
                            <th>Login</th>
                            <th>PIN</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-porteiros"></tbody>
                </table>
            </section>
        </div>

        <div id="historico-tab" class="tab-content">
            <h2>📜 Histórico de Movimentações</h2>
            <section id="filtros-historico" style="background: #f4f4f4; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
                <input type="date" id="filtro-data-inicio">
                <input type="date" id="filtro-data-fim">
                <select id="filtro-empresa">
                    <option value="">Todas Empresas</option>
                    <option value="Correios">Correios</option>
                    <option value="Mercado Livre">Mercado Livre</option>
                    <option value="Shopee">Shopee</option>
                    <option value="Outros">Outros</option>
                </select>
                <button onclick="carregarHistorico()" style="padding: 5px 20px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Filtrar</button>
            </section>
            
            <table id="tabela-historico" style="width: 100%;">
                <thead>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Destinatário/Descrição</th>
                        <th>Empresa</th>
                        <th>Status</th>
                        <th>Detalhes Entrega</th>
                    </tr>
                </thead>
                <tbody id="lista-historico"></tbody>
            </table>
        </div>
    </main>

    <script src="/frontend/js/admin.js"></script>
    <script src="/frontend/js/historico.js"></script>
</body>
</html>