function adicionarLinhaEncomenda() {
    const container = document.getElementById("container-encomendas");
    if (!container) {
        return;
    }

    const novaLinha = document.createElement("div");
    novaLinha.className = "linha-encomenda";
    novaLinha.innerHTML = `
        <input type="text" class="destinatario" placeholder="Destinatário" required>
        <input type="text" class="descricao" placeholder="Descrição do pacote" required>
        <input type="text" class="observacoes" placeholder="Observações do pacote">
        <select class="empresa-transporte" required>
            <option value="">Empresa de transporte...</option>
            <option value="Correios">Correios</option>
            <option value="Mercado Livre">Mercado Livre</option>
            <option value="Shopee">Shopee</option>
            <option value="Temoo">Temoo</option>
            <option value="Aliexpress">Aliexpress</option>
            <option value="Moto Entrega">Moto Entrega Local</option>
            <option value="Outros">Outros</option>
        </select>
        <input type="text" class="entregador" placeholder="Nome entregador" required>
        <button type="button" class="btn-remover" onclick="this.parentElement.remove()">❌</button>
    `;
    container.appendChild(novaLinha);
}

window.adicionarLinhaEncomenda = adicionarLinhaEncomenda;

// Carregar tabela de encomendas ativas para dar baixa
async function carregarListaBaixa() {
    const response = await fetch("/api/encomendas/");
    if (!response.ok) return;

    const encomendas = await response.json();
    const tbody = document.getElementById("lista-baixa");
    tbody.innerHTML = "";

    encomendas.forEach(enc => {
        const tr = document.createElement("tr");
        const dataFormatada = new Date(enc.data_chegada).toLocaleString('pt-BR');
        tr.innerHTML = `
            <td>${enc.id}</td>
            <td>${dataFormatada}</td>            
            <td><strong>${enc.destinatario}</strong></td>
            <td>${enc.descricao}</td>
            <td>${enc.observacoes || '-'}</td>
            <td>${enc.empresa_transporte || '-'}</td>
            <td>${enc.porteiro_graduacao} ${enc.porteiro_nome_guerra}</td>
            <td><button style="background-color: #007bff; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 4px;" onclick="abrirModalBaixa(${enc.id})">Entregar</button></td>
        `;
        tbody.appendChild(tr);
    });
}

// Controle do Modal de Baixa
function abrirModalBaixa(id) {
    document.getElementById("encomenda-id-baixa").value = id;
    document.getElementById("modal-pin").style.display = "block";
    document.getElementById("pin-baixa").value = "";
    document.getElementById("pin-baixa").focus();
}

window.abrirModalBaixa = abrirModalBaixa;

function inicializarPainelOperacao() {
    const formEntrada = document.getElementById("form-entrada");
    const botaoConfirmarBaixa = document.getElementById("btn-confirmar-baixa");

    if (!formEntrada || !botaoConfirmarBaixa) {
        return;
    }

    carregarListaBaixa();

    // Garante que tenha pelo menos uma linha vazia ao carregar a página
    if (document.querySelectorAll(".linha-encomenda").length === 0) {
        adicionarLinhaEncomenda();
    }

    formEntrada.addEventListener("submit", async (e) => {
        e.preventDefault();

        const pin = document.getElementById("pin-entrada").value;
        const linhas = document.querySelectorAll(".linha-encomenda");
        const encomendas = [];

        linhas.forEach(linha => {
            encomendas.push({
                destinatario: linha.querySelector(".destinatario").value,
                descricao: linha.querySelector(".descricao").value,
                observacoes: linha.querySelector(".observacoes").value,
                empresa_transporte: linha.querySelector(".empresa-transporte").value
            });
        });

        if (encomendas.length === 0) {
            alert("Adicione pelo menos uma encomenda antes de dar entrada.");
            return;
        }

        const response = await fetch("/api/encomendas/lote", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ encomendas, pin })
        });

        if (response.ok) {
            formEntrada.reset();
            document.getElementById("container-encomendas").innerHTML = "";
            adicionarLinhaEncomenda();
            carregarListaBaixa();
            alert("Lote de encomendas registrado com sucesso!");
        } else {
            const error = await response.json();
            alert("Erro: " + (error.detail || "Falha ao registrar encomendas. Verifique o PIN."));
        }
    });

    botaoConfirmarBaixa.addEventListener("click", async () => {
        const pin = document.getElementById("pin-baixa").value;
        const recebedor_nome = document.getElementById("recebedor-nome").value;
        const observacao_baixa = document.getElementById("obs-baixa").value;

        if (!pin || !recebedor_nome) {
            alert("PIN e Nome do Recebedor são obrigatórios.");
            return;
        }

        const id = document.getElementById("encomenda-id-baixa").value;
        const response = await fetch(`/api/encomendas/${id}/baixa`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pin, recebedor_nome, observacao_baixa })
        });

        if (response.ok) {
            document.getElementById("modal-pin").style.display = "none";
            carregarListaBaixa();
        } else {
            const error = await response.json();
            alert("Erro: " + (error.detail || "Falha ao dar baixa. Verifique o PIN."));
        }
    });
}

document.addEventListener("DOMContentLoaded", inicializarPainelOperacao);