const API = '/back/api/jobs.php';
const API_POST = '/back/api/applications.php';
const API_AUTH = '/back/api/auth.php';
let annonces = [];
let annoncesFiltrees = [];
let page = 1;
const parPage = 5;

function updateNavigation() {
    fetch(API_AUTH)
        .then(response => response.json())
        .then(data => {
            const profileLink = document.getElementById('profile-link');
            const adminLink = document.getElementById('admin-link');
            const signupLink = document.getElementById('signup-link');
            const loginLink = document.getElementById('login-link');
            
            if (data.logged_in) {
                if (profileLink) profileLink.style.display = 'inline';
                
                if (adminLink && data.user && data.user.role === 'admin') {
                    adminLink.style.display = 'inline';
                } else if (adminLink) {
                    adminLink.style.display = 'none';
                }
                
                if (signupLink) signupLink.style.display = 'none';
                if (loginLink) loginLink.style.display = 'none';
            } else {
                if (profileLink) profileLink.style.display = 'none';
                if (adminLink) adminLink.style.display = 'none';
                
                if (signupLink) signupLink.style.display = 'inline';
                if (loginLink) loginLink.style.display = 'inline';
            }
        })
        .catch(() => {});
}

document.addEventListener('DOMContentLoaded', function() {
    updateNavigation();
    
    fetch(API)
        .then(response => response.json())
        .then(data => {
            annonces = data;
            annoncesFiltrees = annonces;
            afficherAnnonces();
        })
        .catch(error => {
            console.error('Erreur lors du chargement des offres:', error);
        });
});

function afficherAnnonces() {
    const debut = (page - 1) * parPage;
    const fin = debut + parPage;
    const total = Math.ceil(annoncesFiltrees.length / parPage);

    const container = document.querySelector('.offres');
    if (!container) return;
    
    container.innerHTML = `<h2>Offres d'emploi (${annoncesFiltrees.length} trouvées)</h2>`;

    annoncesFiltrees.slice(debut, fin).forEach(annonce => {
        const div = document.createElement('div');
        div.className = 'annonce';
        div.innerHTML = `
            <h3>${annonce.titre}</h3>
            <p>${annonce.entreprise_nom} • ${annonce.lieu}</p>
            <div class="buttons">
                <button class="btn-secondary btn-small" onclick="detail(${annonce.id_annonce})">Détails</button>
                <button class="btn-success btn-small" onclick="postuler(${annonce.id_annonce})">Postuler</button>
            </div>
        `;
        container.appendChild(div);
    });

    if (total > 1) {
        const pagination = document.createElement('div');
        pagination.className = 'pagination';
        pagination.innerHTML = `
            <button ${page === 1 ? 'disabled' : ''} onclick="page--; afficherAnnonces();">Précédent</button>
            <span>Page ${page} sur ${total}</span>
            <button ${page === total ? 'disabled' : ''} onclick="page++; afficherAnnonces();">Suivant</button>
        `;
        container.appendChild(pagination);
    }
}

function detail(id) {
    const annonce = annonces.find(a => a.id_annonce == id);
    if (!annonce) return alert('Annonce introuvable');
    
    document.querySelector('.detail').innerHTML = `
        <h2>${annonce.titre}</h2>
        <p><strong>${annonce.entreprise_nom}</strong></p>
        <p>${annonce.description}</p>
        <p><strong>Lieu:</strong> ${annonce.lieu}</p>
        <p><strong>Type de contrat:</strong> ${annonce.type_contrat}</p>
        <p><strong>Salaire:</strong> ${annonce.salaire}€</p>
        <p><strong>Compétences:</strong> ${annonce.competence}</p>
        <button onclick="postuler(${annonce.id_annonce})">Postuler</button>
    `;
}

let idAnnonceEnCours = null;

function postuler(id) {
    idAnnonceEnCours = id; 
    document.getElementById('formulaire-container').style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('candidature-formulaire');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); 

        if (!confirm('Envoyer votre candidature ?')) return;

        const formData = new FormData(form);
        formData.append('id_annonce', idAnnonceEnCours); 

        fetch('http://localhost:8000/back/api/applications.php', {
            method: 'POST',
            body: formData,
            credentials: 'include' 
        })
        .then(response => {
            if (response.ok) {
                alert('Candidature envoyée avec succès !');
                form.reset(); 
                document.getElementById('formulaire-container').style.display = 'none';
            } else {
                alert('Erreur lors de l\'envoi de la candidature.');
            }
        })
        .catch(error => {
            console.error('Erreur réseau :', error);
            alert('Erreur réseau. Veuillez réessayer plus tard.');
        });
    });
});

function rechercher() {
    const titre = document.getElementById('search-titre').value.toLowerCase();
    const lieu = document.getElementById('search-lieu').value.toLowerCase();

    annoncesFiltrees = annonces.filter(a => 
        (titre === '' || a.titre.toLowerCase().includes(titre) || a.entreprise_nom.toLowerCase().includes(titre)) &&
        (lieu === '' || a.lieu.toLowerCase().includes(lieu))
    );
    page = 1;
    afficherAnnonces();
}

document.getElementById('form-annonce').addEventListener('submit', function(e) {
    e.preventDefault();

    const titre = document.getElementById('titre').value.trim();
    const description = document.getElementById('description').value.trim();
    const lieu = document.getElementById('lieu').value.trim();
    const salaire = document.getElementById('salaire').value ? parseFloat(document.getElementById('salaire').value) : null;
    const type_contrat = document.getElementById('type_contrat').value;
    const adresse = document.getElementById('adresse').value.trim();

    if (!titre || !description || !lieu || !type_contrat || !adresse) {
        alert('Veuillez remplir tous les champs obligatoires.');
        return;
    }

    const data = { titre, description, lieu, salaire, type_contrat, adresse };

    fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('Annonce publiée avec succès !');
            return fetch(API);
        } else {
            throw new Error(data.message || 'Erreur inconnue');
        }
    })
    .then(res => res.json())
    .then(data => {
        annonces = data;
        annoncesFiltrees = annonces;
        afficherAnnonces();
        this.reset();
    })
    .catch(err => alert('Erreur lors de la publication : ' + err.message));
});