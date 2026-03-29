// Conecta ao WebSocket usando o mesmo host/porta da página atual
const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = function(event) {
    // Quando o backend enviar qualquer sinal, recarregamos a lista
    carregarEncomendas();
};

async function carregarEncomendas() {
    try {
        const response = await fetch('/api/encomendas/');
        if (!response.ok) return;
        
        const encomendas = await response.json();
        const tbody = document.getElementById('lista-encomendas');
        tbody.innerHTML = ''; // Limpa a tabela atual
        
        encomendas.forEach(enc => {
            const tr = document.createElement('tr');
            const dataFormatada = new Date(enc.data_chegada).toLocaleString('pt-BR');
            tr.innerHTML = `
                <td><strong>${enc.destinatario}</strong></td>
                <td>${enc.descricao}</td>
                <td>${enc.observacoes || '-'}</td>
                <td>${enc.empresa_transporte || '-'}</td>
                <td>${dataFormatada}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Erro ao buscar encomendas:", error);
    }
}

// Carrega o estado atual assim que a página abre
window.onload = carregarEncomendas;