document.addEventListener("DOMContentLoaded", () => {
    carregarPorteiros();
});

// Cadastrar novo Porteiro
document.getElementById("form-admin").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const graduacao = document.getElementById("porteiro-graduacao").value;
    const nome_guerra = document.getElementById("porteiro-nome-guerra").value;
    const nome_completo = document.getElementById("porteiro-nome").value;
    const login = document.getElementById("porteiro-login").value;
    const pin = document.getElementById("porteiro-pin").value;

    const id = document.getElementById("porteiro-id").value;
    const payload = { graduacao, nome_guerra, nome_completo, login };
    if (pin) payload.pin = pin; // Só envia o PIN se foi preenchido (importante para não sobrescrever com vazio na edição)

    let url = "/api/porteiros/";
    let method = "POST";
    let msgSucesso = "Porteiro cadastrado com sucesso!";

    if (id) {
        url = `/api/porteiros/${id}`;
        method = "PUT";
        msgSucesso = "Porteiro atualizado com sucesso!";
    }

    const response = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    if (response.ok) {
        cancelarEdicao(); // Limpa o form e reseta os botões
        carregarPorteiros();
        alert(msgSucesso);
    } else {
        const error = await response.json();
        alert("Erro: " + (error.detail || "Falha ao cadastrar porteiro."));
    }
});

// Listar Efetivo na Tabela
async function carregarPorteiros() {
    const response = await fetch("/api/porteiros/");
    if (!response.ok) return;

    const porteiros = await response.json();
    const tbody = document.getElementById("tbody-porteiros");
    tbody.innerHTML = "";

    porteiros.forEach(p => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-weight: bold; color: #007bff;">${p.numero_id || p.id}</td>
            <td>${escapeHTML(p.graduacao)}</td>
            <td>${escapeHTML(p.nome_guerra)}</td>
            <td>${escapeHTML(p.nome_completo)}</td>
            <td>${escapeHTML(p.login)}</td>
            <td>****</td> 
            <td>
                <button style="background-color: #ffc107; color: #000; border: none; padding: 5px 10px; cursor: pointer; margin-right: 5px;" onclick="prepararEdicao(${p.id}, '${escapeHTML(p.graduacao)}', '${escapeHTML(p.nome_guerra)}', '${escapeHTML(p.nome_completo)}', '${escapeHTML(p.login)}')">Editar</button>
                <button style="background-color: #dc3545;" onclick="deletarPorteiro(${p.id})">Excluir</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Excluir Porteiro
window.deletarPorteiro = async function(id) {
    if (!confirm("Tem certeza que deseja remover este militar do acesso?")) return;

    const response = await fetch(`/api/porteiros/${id}`, {
        method: "DELETE"
    });

    if (response.ok) {
        carregarPorteiros();
    } else {
        alert("Erro ao excluir porteiro.");
    }
};

window.prepararEdicao = function(id, graduacao, nome_guerra, nome_completo, login) {
    document.getElementById("porteiro-id").value = id;
    document.getElementById("porteiro-graduacao").value = graduacao;
    document.getElementById("porteiro-nome-guerra").value = nome_guerra;
    document.getElementById("porteiro-nome").value = nome_completo;
    document.getElementById("porteiro-login").value = login;
    
    const pinInput = document.getElementById("porteiro-pin");
    pinInput.value = "";
    pinInput.placeholder = "Novo PIN (vazio para manter)";
    pinInput.removeAttribute("required");

    document.getElementById("btn-salvar").textContent = "Atualizar Porteiro";
    document.getElementById("btn-cancelar").style.display = "inline-block";
};

// --- Lógica do Modal de Troca de Senha Admin ---
window.abrirModalSenhaAdmin = function() {
    document.getElementById("admin-senha-atual").value = "";
    document.getElementById("admin-nova-senha").value = "";
    document.getElementById("admin-confirma-senha").value = "";
    document.getElementById("modal-senha-admin").style.display = "block";
};

window.fecharModalSenhaAdmin = function() {
    document.getElementById("modal-senha-admin").style.display = "none";
};

window.salvarSenhaAdmin = async function() {
    const senhaAtual = document.getElementById("admin-senha-atual").value;
    const novaSenha = document.getElementById("admin-nova-senha").value;
    const confirmaSenha = document.getElementById("admin-confirma-senha").value;

    if (!senhaAtual || !novaSenha || !confirmaSenha) {
        alert("Preencha todos os campos.");
        return;
    }

    if (novaSenha !== confirmaSenha) {
        alert("A nova senha e a confirmação não coincidem.");
        return;
    }

    const response = await fetch("/api/admin/senha", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ senha_atual: senhaAtual, nova_senha: novaSenha })
    });

    if (response.ok) {
        alert("Senha alterada com sucesso! Você será desconectado para logar novamente.");
        fazerLogout();
    } else {
        const error = await response.json();
        alert("Erro: " + (error.detail || "Falha ao alterar senha."));
    }
};

window.cancelarEdicao = function() {
    document.getElementById("form-admin").reset();
    document.getElementById("porteiro-id").value = "";
    
    const pinInput = document.getElementById("porteiro-pin");
    pinInput.placeholder = "PIN da Cancela";
    pinInput.setAttribute("required", "true");

    document.getElementById("btn-salvar").textContent = "Salvar Porteiro";
    document.getElementById("btn-cancelar").style.display = "none";
};