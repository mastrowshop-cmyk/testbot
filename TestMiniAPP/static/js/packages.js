async function loadMyPackages() {
    const packagesDiv = document.getElementById('packagesList');
    packagesDiv.innerHTML = '<div style="text-align:center;padding:40px;">Загрузка...</div>';
    
    try {
        const response = await fetch(`/api/packages/${userId}`);
        const packages = await response.json();
        
        if (packages.length === 0) {
            packagesDiv.innerHTML = '<div style="text-align:center;color:var(--text-secondary);">📭 Нет посылок</div>';
            return;
        }
        
        let html = '';
        packages.forEach(pkg => {
            const status = pkg.status === 'готова' ? 'ready' : 'waiting';
            const statusText = pkg.status === 'готова' ? 'ГОТОВА' : 'ОЖИДАЕТ';
            const date = new Date(pkg.added_date).toLocaleDateString('ru-RU');
            
            html += `
                <div class="package-item">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                        <div>
                            <strong>${pkg.track}</strong>
                            <div style="font-size:14px;color:var(--text-secondary);">📅 ${date}</div>
                        </div>
                        <span class="status ${status}">${statusText}</span>
                    </div>
                    <div>
                        <span style="background:rgba(102,126,234,0.2);padding:5px 10px;border-radius:10px;color:var(--accent);">
                            📍 ${pkg.location}
                        </span>
                    </div>
                </div>
            `;
        });
        
        packagesDiv.innerHTML = html;
    } catch (error) {
        packagesDiv.innerHTML = '<div style="color:var(--danger);text-align:center;">⚠️ Ошибка загрузки</div>';
    }
}