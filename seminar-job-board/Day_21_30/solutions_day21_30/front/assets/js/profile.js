// Utilitaires
const $ = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);

// Gestion des bulles
function addBubble(containerId) {
    const container = $(containerId);
    const bubble = document.createElement('div');
    
    if (containerId === 'competences-list') {
        bubble.className = 'competence-bubble';
        bubble.innerHTML = `<div class="bubble-content">À renseigner</div><div class="bubble-actions"><button class="bubble-delete" onclick="removeBubble(this)"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3,6 5,6 21,6"></polyline><path d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path></svg></button></div>`;
    } else {
        const type = containerId.includes('experience') ? 'experience' : 'formation';
        bubble.className = `${type}-bubble`;
        bubble.innerHTML = `<div class="${type}-fields">
            <input type="text" class="${type}-title" placeholder="${type === 'experience' ? 'Titre du poste' : 'Titre de la formation'}" value="">
            <div class="${type}-details">
                <input type="text" class="${type}-date" placeholder="Date" value="">
                <input type="text" class="${type}-location" placeholder="Lieu" value="">
            </div>
            <textarea class="${type}-description" placeholder="Description" rows="2"></textarea>
        </div><div class="bubble-actions"><button class="bubble-delete" onclick="removeBubble(this)"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3,6 5,6 21,6"></polyline><path d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path></svg></button></div>`;
    }
    container.appendChild(bubble);
}

function removeBubble(button) {
    button.closest('.experience-bubble, .formation-bubble, .competence-bubble').remove();
}

// Données profil
function getProfileData() {
    const nameParts = $('profile-name').textContent.split(' ');
    return {
        prenom: nameParts[0] || '',
        nom: nameParts.slice(1).join(' ') || '',
        email: $('profile-email').textContent,
        telephone: $('profile-phone').textContent,
        adresse: $('profile-address').textContent,
        experiences: getBubbleData('experiences-list'),
        formation: getBubbleData('formations-list'),
        competences: getBubbleData('competences-list'),
        photo_profil: $('profile-photo').querySelector('img')?.src || ''
    };
}

function getBubbleData(containerId) {
    const bubbles = $$(`#${containerId} .experience-bubble, #${containerId} .formation-bubble, #${containerId} .competence-bubble`);
    return Array.from(bubbles).map(bubble => {
        const content = bubble.querySelector('.bubble-content');
        if (content) return content.textContent.trim();
        
        const title = bubble.querySelector('.experience-title, .formation-title')?.value || '';
        const date = bubble.querySelector('.experience-date, .formation-date')?.value || '';
        const location = bubble.querySelector('.experience-location, .formation-location')?.value || '';
        const description = bubble.querySelector('.experience-description, .formation-description')?.value || '';
        
        return `${title} | ${date} | ${location} | ${description}`;
    }).filter(data => data && !data.includes('À renseigner') && data !== ' |  |  | ').join(' || ');
}

function loadBubbleData(containerId, data) {
    if (!data || data === 'À renseigner') return;
    
    const items = data.split(' || ').filter(item => item.trim());
    if (items.length === 0) return;
    
    const container = $(containerId);
    const firstBubble = container.querySelector('.experience-bubble, .formation-bubble, .competence-bubble');
    
    if (firstBubble && items[0]) {
        const parts = items[0].split(' | ');
        if (containerId === 'competences-list') {
            firstBubble.querySelector('.bubble-content').textContent = parts[0];
        } else if (parts.length >= 4) {
            const [title, date, location, description] = parts;
            firstBubble.querySelector('.experience-title, .formation-title').value = title;
            firstBubble.querySelector('.experience-date, .formation-date').value = date;
            firstBubble.querySelector('.experience-location, .formation-location').value = location;
            firstBubble.querySelector('.experience-description, .formation-description').value = description;
        }
    }
    
    items.slice(1).forEach(item => {
        addBubble(containerId);
        const newBubble = container.lastElementChild;
        const parts = item.split(' | ');
        
        if (containerId === 'competences-list') {
            newBubble.querySelector('.bubble-content').textContent = parts[0];
        } else if (parts.length >= 4) {
            const [title, date, location, description] = parts;
            newBubble.querySelector('.experience-title, .formation-title').value = title;
            newBubble.querySelector('.experience-date, .formation-date').value = date;
            newBubble.querySelector('.experience-location, .formation-location').value = location;
            newBubble.querySelector('.experience-description, .formation-description').value = description;
        }
    });
}

// Chargement profil
function loadProfile() {
    fetch('/back/api/auth.php', { credentials: 'include' })
        .then(r => r.json())
        .then(data => {
            if (!data.logged_in) return window.location.href = 'login.html';
            
            const user = data.user;
            $('profile-name').textContent = user.name;
            $('profile-email').textContent = user.email;
            $('profile-phone').textContent = user.telephone || 'Non renseigné';
            $('profile-address').textContent = user.adresse || 'Non renseigné';
            
            loadBubbleData('experiences-list', user.experiences);
            loadBubbleData('formations-list', user.formation || user.etudes);
            loadBubbleData('competences-list', user.competences);
            
            if (user.photo_profil) {
                const photoContainer = $('profile-photo');
                photoContainer.querySelector('.profile-photo-placeholder')?.remove();
                const img = photoContainer.querySelector('img') || document.createElement('img');
                img.src = user.photo_profil;
                photoContainer.appendChild(img);
            }
            
            // Initialiser en mode lecture seule
            document.querySelectorAll('#profile-name, #profile-email, #profile-phone, #profile-address').forEach(el => el.contentEditable = false);
            document.querySelectorAll('.bubble-content, input, textarea').forEach(el => {
                el.contentEditable = false;
                if (el.readOnly !== undefined) el.readOnly = true;
            });
            document.querySelectorAll('.bubble-actions').forEach(el => { el.style.opacity = '0'; el.style.visibility = 'hidden'; });
            document.querySelectorAll('.add-btn, .action-btn').forEach(el => el.style.display = 'none');
            
            $('loading-profile').style.display = 'none';
            $('profile-content').style.display = 'block';
        });
}

// Mode édition
let isEditMode = false;

function toggleEdit() {
    const btn = document.querySelector('button[onclick="toggleEdit()"]');
    const logoutBtn = document.querySelector('button[onclick="logout()"]');
    
    if (!isEditMode) {
        // Mode édition ON
        isEditMode = true;
        document.querySelectorAll('#profile-name, #profile-email, #profile-phone, #profile-address').forEach(el => el.contentEditable = true);
        document.querySelectorAll('.bubble-content, input, textarea').forEach(el => {
            el.contentEditable = true;
            if (el.readOnly !== undefined) el.readOnly = false;
        });
        document.querySelectorAll('.bubble-actions').forEach(el => { el.style.opacity = '1'; el.style.visibility = 'visible'; });
        document.querySelectorAll('.add-btn, .action-btn').forEach(el => el.style.display = 'block');
        
        logoutBtn.style.display = 'none';
        btn.textContent = 'Supprimer le compte';
        btn.className = 'btn-danger';
        btn.onclick = deleteUser;
        
        const saveBtn = document.createElement('button');
        saveBtn.textContent = 'Sauvegarder';
        saveBtn.className = 'btn-primary';
        saveBtn.style.marginRight = '12px';
        saveBtn.onclick = saveProfile;
        btn.parentNode.insertBefore(saveBtn, btn);
    } else {
        // Mode édition OFF
        isEditMode = false;
        document.querySelectorAll('#profile-name, #profile-email, #profile-phone, #profile-address').forEach(el => el.contentEditable = false);
        document.querySelectorAll('.bubble-content, input, textarea').forEach(el => {
            el.contentEditable = false;
            if (el.readOnly !== undefined) el.readOnly = true;
        });
        document.querySelectorAll('.bubble-actions').forEach(el => { el.style.opacity = '0'; el.style.visibility = 'hidden'; });
        document.querySelectorAll('.add-btn, .action-btn').forEach(el => el.style.display = 'none');
        
        logoutBtn.style.display = 'inline-block';
        btn.textContent = 'Modifier';
        btn.className = 'btn-primary';
        btn.onclick = toggleEdit;
        
        const saveBtn = btn.parentNode.querySelector('button[onclick="saveProfile"]');
        if (saveBtn) saveBtn.remove();
    }
}

function saveProfile() {
    fetch('/back/api/auth.php', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(getProfileData())
    }).then(() => location.reload());
}

// Photo
function editPhoto() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const photoContainer = $('profile-photo');
            photoContainer.querySelector('.profile-photo-placeholder')?.remove();
            const img = photoContainer.querySelector('img') || document.createElement('img');
            img.src = e.target.result;
            photoContainer.appendChild(img);
            
            const userData = getProfileData();
            userData.photo_profil = e.target.result;
            
            fetch('/back/api/auth.php', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(userData)
            });
        };
        reader.readAsDataURL(file);
    };
    input.click();
}

// Auth
function logout() {
    fetch('/back/api/auth.php', { method: 'DELETE', credentials: 'include' })
        .then(() => window.location.href = 'login.html');
}

function deleteUser() {
    if (confirm('Supprimer le compte ?')) {
        fetch('/back/api/users.php', { method: 'DELETE', credentials: 'include' })
            .then(() => window.location.href = 'index.html');
    }
}

document.addEventListener('DOMContentLoaded', loadProfile);