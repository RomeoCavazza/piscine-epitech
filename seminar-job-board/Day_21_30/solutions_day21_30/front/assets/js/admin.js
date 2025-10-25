let currentTable = 'Users';

function showTab(table) {
    currentTable = table;
    document.getElementById('table-title').textContent = table;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    load();
}

function load() {
    fetch(`/back/api/admin.php?table=${currentTable}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) return alert('Erreur: ' + data.error);
            
            if (!data.data || data.data.length === 0) {
                document.getElementById('table-head').innerHTML = '<tr><th>Aucune donnée</th></tr>';
                document.getElementById('table-body').innerHTML = '<tr><td>Aucune donnée disponible</td></tr>';
                return;
            }
            
            const headers = Object.keys(data.data[0]);
            document.getElementById('table-head').innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}<th>Actions</th></tr>`;
            document.getElementById('table-body').innerHTML = data.data.map(row => {
                const cells = headers.map(h => {
                    if (h.toLowerCase().includes('logo') || h.toLowerCase().includes('image')) {
                        return `<td class="logo-cell">${row[h] ? `<img src="${row[h]}" alt="Logo" onerror="this.style.display='none'">` : ''}</td>`;
                    }
                    return `<td>${row[h] || ''}</td>`;
                }).join('');
                return `<tr>${cells}<td class="actions-cell">
                    <button onclick="edit(${row[headers[0]]})" title="Modifier">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                    </button>
                    <button onclick="del(${row[headers[0]]})" title="Supprimer">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3,6 5,6 21,6"></polyline>
                            <path d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                        </svg>
                    </button>
                </td></tr>`;
            }).join('');
        })
        .catch(error => alert('Erreur: ' + error.message));
}

function add() {
    alert('Fonctionnalité d\'ajout non implémentée');
}

function edit(id) {
    alert('Fonctionnalité d\'édition non implémentée');
}

function del(id) {
    if (confirm('Supprimer cet élément ?')) {
        fetch('/back/api/admin.php', {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({table: currentTable, id: id})
        })
        .then(r => r.json())
        .then(result => {
            if (result.success) {
                load();
            } else {
                alert('Erreur lors de la suppression');
            }
        });
    }
}

load();