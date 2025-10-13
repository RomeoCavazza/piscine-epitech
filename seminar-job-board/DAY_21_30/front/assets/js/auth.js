function showNav() {
    const nav = document.querySelector('nav');
    if (!nav) return;
    
    const isProfile = window.location.pathname.includes('profile.html');
    const authButtons = `<button onclick="showSignIn()" class="btn-signin">Sign in</button><button onclick="showSignUp()" class="btn-signup">Sign up</button>`;
    
    api('auth.php').then(data => {
        if (data.logged_in) {
            nav.innerHTML = isProfile ? `<a href="index.html">Offres</a>` : `<a href="profile.html">Profil</a>`;
            if (isProfile && window.loadProfile) window.loadProfile();
        } else {
            nav.innerHTML = authButtons;
            if (isProfile) window.location.href = 'index.html';
        }
    }).catch(() => {
        nav.innerHTML = authButtons;
        if (isProfile) window.location.href = 'index.html';
    });
}

function handleAuth(event, endpoint) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    api(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    })
    .then(data => {
        if (data.success) {
            closeModal();
            showNotification('OK', 'success');
            showNav();
            if (endpoint === 'users.php') setTimeout(() => window.location.href = 'index.html', 1000);
        } else showNotification(data.error, 'error');
    })
    .catch(() => showNotification('Erreur', 'error'));
    return false;
}

function logout() {
    api('auth.php', {method: 'DELETE'})
        .then(() => {showNotification('Déconnecté', 'success'); setTimeout(() => window.location.href = 'index.html', 500);});
}

document.addEventListener('DOMContentLoaded', showNav);