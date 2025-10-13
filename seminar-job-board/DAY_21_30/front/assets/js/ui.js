function showNotification(message, type = 'info', duration = 3000) {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `<div class="notification-message">${message}</div><button class="notification-close" onclick="closeNotification(this)">&times;</button>`;
    
    container.appendChild(notification);
    if (duration > 0) setTimeout(() => closeNotification(notification.querySelector('.notification-close')), duration);
}

function closeNotification(button) {
    const notification = button.parentElement;
    notification.style.animation = 'slideOut 0.3s ease-in forwards';
    setTimeout(() => {if (notification.parentElement) notification.parentElement.removeChild(notification);}, 300);
}

function showSignIn() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Sign in</h2>
            <form onsubmit="return handleAuth(event, 'auth.php')">
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="mot_de_passe" placeholder="Mot de passe" required>
                <button type="submit" class="btn-primary">Se connecter</button>
                <button type="button" onclick="closeModal()" class="btn-secondary">Annuler</button>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
}

function showSignUp() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-height: 90vh; overflow-y: auto;">
            <h2>Sign up</h2>
            <form onsubmit="return handleAuth(event, 'users.php')">
                <input type="text" name="prenom" placeholder="Prénom" required>
                <input type="text" name="nom" placeholder="Nom" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="mot_de_passe" placeholder="Mot de passe" required>
                <input type="date" name="date_naissance" placeholder="Date de naissance">
                <input type="text" name="adresse" placeholder="Adresse">
                <input type="text" name="etudes" placeholder="Études">
                <input type="tel" name="telephone" placeholder="Téléphone">
                <select name="roles" required>
                    <option value="">-- Choisir un rôle --</option>
                    <option value="candidat">Candidat</option>
                    <option value="recruteur">Recruteur</option>
                </select>
                <button type="submit" class="btn-primary">S'inscrire</button>
                <button type="button" onclick="closeModal()" class="btn-secondary">Annuler</button>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}