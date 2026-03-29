async function carregarHistorico() {
    const dataInicio = document.getElementById("filtro-data-inicio").value;
    const dataFim = document.getElementById("filtro-data-fim").value;
    const empresa = document.getElementById("filtro-empresa").value;
    const status = document.getElementById("filtro-status")?.value || "";

    // Monta a Query String para filtros
    let url = `/api/historico?`;
    if (dataInicio) url += `data_inicio=${dataInicio}&`;
    if (dataFim) url += `data_fim=${dataFim}&`;
    if (status) url += `status=${status}&`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Erro ao buscar histórico");

        const dados = await response.json();
        const tbody = document.getElementById("lista-historico");
        tbody.innerHTML = "";

        dados.forEach(enc => {
            // Filtro local para empresa (opcional, se não feito no backend)
            if (empresa && enc.empresa_transporte !== empresa) return;

            const tr = document.createElement("tr");
            const dataChegada = new Date(enc.data_chegada).toLocaleString('pt-BR');
            const dataEntrega = enc.data_entrega ? new Date(enc.data_entrega).toLocaleString('pt-BR') : "-";
            
            tr.innerHTML = `
                <td>
                    <strong>Chegada:</strong> ${dataChegada}<br>
                    <small>Entrega: ${dataEntrega}</small>
                </td>
                <td>
                    <strong>${enc.destinatario}</strong><br>
                    <small>${enc.descricao}</small>
                </td>
                <td>${enc.empresa_transporte}</td>
                <td>
                    <span class="status-badge ${enc.status === 'Entregue' ? 'status-verde' : 'status-azul'}">
                        ${enc.status}
                    </span>
                </td>
                <td>
                    <strong>${enc.recebedor_nome || "-"}</strong><br>
                    <small>${enc.observacao_baixa || ""}</small>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Erro:", error);
    }
}

// Função para alternar abas (deve estar disponível globalmente)
function switchTab(tabId) {
    // Esconde todos os conteúdos
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    // Desativa todos os botões
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Ativa a aba selecionada
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');

    // Se a aba for a de histórico, carrega os dados automaticamente
    if (tabId === 'historico-tab') {
        carregarHistorico();
    }
}

window.switchTab = switchTab;
window.carregarHistorico = carregarHistorico;