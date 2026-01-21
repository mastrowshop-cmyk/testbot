const tg = window.Telegram.WebApp;
tg.expand();
let userId = null;
let userData = null;

document.addEventListener('DOMContentLoaded', async function() {
    const urlParams = new URLSearchParams(window.location.search);
    userId = urlParams.get('user_id');
    if (!userId) {
        document.body.innerHTML = '<h1 style="text-align:center;padding:40px;">🔒 Откройте через Telegram бота</h1>';
        return;
    }
    await loadUserData();
});

async function loadUserData() {
    try {
        const response = await fetch(`/api/user/${userId}`);
        userData = await response.json();
        document.getElementById('userWelcome').innerHTML = `👤 ${userData.name} • 📱 ${userData.phone}`;
    } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
    }
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById(tabName + 'Tab').style.display = 'block';
    event.target.classList.add('active');
    if (tabName === 'packages') loadMyPackages();
    else if (tabName === 'profile') loadProfile();
}