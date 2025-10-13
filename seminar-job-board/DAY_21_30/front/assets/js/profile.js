window.loadProfile = function() {
    api('users.php').then(data => {
            if (data.success) {
                const user = data.user;
                document.getElementById('loading-profile').style.display = 'none';
                document.getElementById('profile-content').style.display = 'block';
                
                document.getElementById('profile-name').textContent = `${user.prenom} ${user.nom}`;
                document.getElementById('profile-role').textContent = user.roles;
                document.getElementById('profile-email').textContent = user.email;
                document.getElementById('profile-role-display').textContent = user.roles;
                document.getElementById('profile-address').textContent = user.adresse || 'Non renseigné';
                document.getElementById('profile-education').textContent = user.etudes || 'Non renseigné';
                document.getElementById('profile-phone').textContent = user.telephone || 'Non renseigné';

                ['prenom', 'nom', 'adresse', 'etudes', 'telephone'].forEach(field => document.getElementById(field).value = user[field] || '');

                if (user.roles === 'recruteur') {
                    document.getElementById('company-section').style.display = 'block';
                    window.currentCompany = data.company;
                    loadCompany();
                }
            }
        })
        .catch(() => showNotification('Erreur', 'error'));
};

function editProfile() {
    document.getElementById('profile-info').style.display = 'none';
    document.getElementById('profile-form').style.display = 'block';
}

function cancelEdit() {
    document.getElementById('profile-form').style.display = 'none';
    document.getElementById('profile-info').style.display = 'block';
}

function updateProfile(event) {
    event.preventDefault();
    return saveForm(event, cancelEdit);
}

function loadCompany() {
    const div = document.getElementById('company-info');
    const c = window.currentCompany;
    if (c) {
        div.innerHTML = `<h2>Entreprise</h2><div class="profile-grid"><div class="profile-item"><strong>Nom</strong><span>${c.nom}</span></div><div class="profile-item"><strong>Secteur</strong><span>${c.secteur || 'Non renseigné'}</span></div><div class="profile-item"><strong>Adresse</strong><span>${c.adresse || 'Non renseigné'}</span></div><div class="profile-item"><strong>Email</strong><span>${c.email || 'Non renseigné'}</span></div></div><div class="profile-actions"><button onclick="showCompanyForm()" class="btn-primary">Modifier</button></div>`;
        ['nom_entreprise', 'secteur', 'adresse_entreprise', 'email_entreprise'].forEach(f => document.getElementById(f).value = c[f.replace('_entreprise', '').replace('entreprise', 'nom')] || '');
    } else {
        div.innerHTML = `<h2>Entreprise</h2><p>Aucune entreprise.</p><div class="profile-actions"><button onclick="showCompanyForm()" class="btn-primary">Créer</button></div>`;
    }
}

function showCompanyForm() {toggleForm('company-info', 'company-form');}
function cancelCompanyEdit() {toggleForm('company-form', 'company-info');}
function updateCompany(event) {event.preventDefault(); return saveForm(event, cancelCompanyEdit);}

function toggleForm(hide, show) {
    document.getElementById(hide).style.display = 'none';
    document.getElementById(show).style.display = 'block';
}

function saveForm(event, callback) {
    api('users.php', {method: 'POST', body: JSON.stringify(Object.fromEntries(new FormData(event.target)))})
        .then(data => {
            if (data.success) {showNotification('OK', 'success'); callback(); loadProfile();}
            else showNotification(data.error, 'error');
        });
    return false;
}