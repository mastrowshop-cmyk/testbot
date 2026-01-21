function loadProfile() {
    if (!userData) return;
    const profileDiv = document.getElementById('profileInfo');
    profileDiv.innerHTML = `
        <div style="margin-bottom:30px;">
            <div style="margin-bottom:15px;">
                <div style="color:var(--text-secondary);">Имя</div>
                <div style="font-size:18px;">${userData.name}</div>
            </div>
            <div style="margin-bottom:15px;">
                <div style="color:var(--text-secondary);">Телефон</div>
                <div style="font-size:18px;">${userData.phone}</div>
            </div>
            <div style="margin-bottom:15px;">
                <div style="color:var(--text-secondary);">Код клиента</div>
                <div style="font-size:18px;">${userData.client_code}</div>
            </div>
            <div style="margin-bottom:15px;">
                <div style="color:var(--text-secondary);">Дата регистрации</div>
                <div style="font-size:18px;">${new Date(userData.registered).toLocaleDateString('ru-RU')}</div>
            </div>
        </div>
    `;
}