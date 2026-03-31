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
            <td><strong>${escapeHTML(enc.destinatario)}</strong></td>
            <td>${escapeHTML(enc.descricao)}</td>
            <td>${escapeHTML(enc.observacoes || '-')}</td>
            <td>${escapeHTML(enc.empresa_transporte || '-')}</td>
            <td>${escapeHTML(enc.porteiro_graduacao)} ${escapeHTML(enc.porteiro_nome_guerra)}</td>
            <td>
                <button style="background-color: #007bff; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 4px; margin-right: 5px;" onclick="abrirModalBaixa(${enc.id})">Entregar</button>
                <button style="background-color: #dc3545; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 4px;" onclick="abrirModalCancelar(${enc.id})" title="Excluir Registro">✖</button>
            </td>
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

function abrirModalCancelar(id) {
    document.getElementById("encomenda-id-cancelar").value = id;
    document.getElementById("modal-cancelar").style.display = "block";
    document.getElementById("motivo-cancelar").value = "";
    document.getElementById("pin-cancelar").value = "";
    document.getElementById("motivo-cancelar").focus();
}

window.abrirModalCancelar = abrirModalCancelar;

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
                empresa_transporte: linha.querySelector(".empresa-transporte").value,
                entregador: linha.querySelector(".entregador").value
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

    const botaoConfirmarCancelar = document.getElementById("btn-confirmar-cancelar");
    if (botaoConfirmarCancelar) {
        botaoConfirmarCancelar.addEventListener("click", async () => {
            const pin = document.getElementById("pin-cancelar").value;
            const motivo = document.getElementById("motivo-cancelar").value;

            if (!pin || !motivo) {
                alert("O PIN e o Motivo são obrigatórios para exclusão.");
                return;
            }

            const id = document.getElementById("encomenda-id-cancelar").value;
            const response = await fetch(`/api/encomendas/${id}/cancelar`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pin, motivo })
            });

            if (response.ok) {
                document.getElementById("modal-cancelar").style.display = "none";
                carregarListaBaixa();
            } else {
                const error = await response.json();
                alert("Erro: " + (error.detail || "Falha ao excluir. Verifique o PIN."));
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", inicializarPainelOperacao);

async function abrirModalIDs() {
    const modal = document.getElementById('modal-lista-ids');
    const tbody = document.getElementById('corpo-tabela-ids');
    modal.style.display = 'flex';
    
    try {
        const response = await fetch('/api/porteiros/publico'); // Criaremos esta rota simples
        const porteiros = await response.json();
        
        tbody.innerHTML = porteiros.map(p => `
            <tr>
                <td style="font-weight:bold; color:#007bff; font-size:1.2em;">${p.numero_id}</td>
                <td>${p.graduacao} ${p.nome_guerra}</td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = "<tr><td colspan='2'>Erro ao carregar lista.</td></tr>";
    }
}