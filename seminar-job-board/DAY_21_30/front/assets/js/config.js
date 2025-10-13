const API = `http://localhost:${window.location.port}/back/api`;

function api(endpoint, options = {}) {
    return fetch(`${API}/${endpoint}`, {
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        ...options
    }).then(r => r.json());
}
