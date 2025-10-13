let annonces = [], annoncesOriginales = [], page = 1, parPage = 5;

function loadJobs() {
    api('jobs.php').then(data => {
        annoncesOriginales = data; 
        annonces = data; 
        afficherAnnonces();
    });
}

function afficherAnnonces() {
    const debut = (page - 1) * parPage, fin = debut + parPage, total = Math.ceil(annonces.length / parPage);
    const container = document.querySelector('.offres');
    if (!container) return;
    
    container.innerHTML = '<h2>Offres d\'emploi</h2>' + annonces.slice(debut, fin).map(annonce => `
        <div class="annonce">
            <h3>${annonce.titre}</h3>
            <p>${annonce.entreprise_nom || 'Entreprise non spécifiée'} • ${annonce.lieu}</p>
            <div class="buttons">
                <button class="btn-secondary btn-small" onclick="detail(${annonce.id_annonce})">Détails</button>
            </div>
        </div>
    `).join('');

    if (total > 1) container.innerHTML += `
        <div class="pagination">
            <button ${page === 1 ? 'disabled' : ''} onclick="previousPage()">Précédent</button>
            <span>Page ${page} sur ${total}</span>
            <button ${page === total ? 'disabled' : ''} onclick="nextPage()">Suivant</button>
        </div>
    `;
}

function detail(id) {
    const annonce = annonces.find(a => a.id_annonce == id);
    const container = document.querySelector('.detail');
    if (!container) return;
    container.innerHTML = `
        <h2>${annonce.titre}</h2>
        <p><strong>${annonce.entreprise_nom || 'Entreprise non spécifiée'}</strong></p>
        <p>${annonce.description}</p>
        <p><strong>Lieu:</strong> ${annonce.lieu}</p>
        <p><strong>Type:</strong> ${annonce.type_contrat || 'Non spécifié'}</p>
        <p><strong>Salaire:</strong> ${annonce.salaire ? annonce.salaire + '€' : 'Non spécifié'}</p>
        ${annonce.competence ? `<p><strong>Compétences:</strong> ${annonce.competence}</p>` : ''}
        <button onclick="postuler(${annonce.id_annonce})" class="btn-primary">Postuler</button>
    `;
}

function postuler(id) {
    if (!confirm('Postuler ?')) return;
    api('applications.php', {method: 'POST', body: JSON.stringify({id_annonce: id})})
        .then(() => showNotification('Envoyé !', 'success'));
}

function rechercher() {
    const titre = document.getElementById('search-titre').value.toLowerCase();
    const lieu = document.getElementById('search-lieu').value.toLowerCase();
    annonces = annoncesOriginales.filter(a => 
        (titre === '' || a.titre.toLowerCase().includes(titre) || (a.entreprise_nom && a.entreprise_nom.toLowerCase().includes(titre))) &&
        (lieu === '' || a.lieu.toLowerCase().includes(lieu))
    );
    page = 1;
    afficherAnnonces();
}

function previousPage() {if (page > 1) {page--; afficherAnnonces();}}
function nextPage() {const total = Math.ceil(annonces.length / parPage); if (page < total) {page++; afficherAnnonces();}}

if (window.location.pathname.includes('index.html') || window.location.pathname === '/') loadJobs();