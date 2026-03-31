// Interceptador Global de Requisições (Segurança 80/20) e Helper XSS
const originalFetch = window.fetch;
window.fetch = async function() {
    let [resource, config] = arguments;
    
    if (!config) config = {};
    if (!config.headers) config.headers = {};
    
    // Injeta o token em todas as requisições (exceto login)
    const token = sessionStorage.getItem('userToken');
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await originalFetch(resource, config);
    
    // Se o Backend rejeitar por falta de permissão ou token inválido
    if (response.status === 401 || response.status === 403) {
        if (typeof resource === 'string' && !resource.includes('/api/login')) {
            alert("Sessão expirada ou acesso negado. Faça login novamente.");
            sessionStorage.clear();
            // window.parent garante que saia mesmo se estiver dentro do iframe (histórico)
            window.parent.location.href = '/frontend/login.html'; 
        }
    }
    return response;
};

// Sanitizador Global (Preparação para mitigar XSS no próximo passo)
window.escapeHTML = function(str) {
    if (str === null || str === undefined) return '';
    return String(str).replace(/[&<>'"]/g, function(tag) {
        const charsToReplace = { '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' };
        return charsToReplace[tag] || tag;
    });
};