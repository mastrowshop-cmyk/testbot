async function searchTrack() {
    const track = document.getElementById('trackInput').value.trim().toUpperCase();
    if (track.length < 6) { alert("Минимум 6 символов"); return; }
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '<div style="text-align:center;padding:40px;">🔍 Поиск...</div>';
    
    try {
        const response = await fetch(`/api/search/${track}?user_id=${userId}`);
        const data = await response.json();
        if (data.found) {
            resultsDiv.innerHTML = `
                <div style="background:rgba(76,175,80,0.1);padding:25px;border-radius:15px;border:1px solid var(--success);">
                    <h3 style="color:var(--success);">✅ НАЙДЕНА!</h3>
                    <p><strong>Трек:</strong> ${data.track}</p>
                    <p><strong>Место:</strong> ${data.location}</p>
                    <p>Добавлено в ваш список</p>
                </div>
            `;
            setTimeout(() => loadMyPackages(), 1000);
        } else {
            resultsDiv.innerHTML = `
                <div style="background:rgba(244,67,54,0.1);padding:25px;border-radius:15px;border:1px solid var(--danger);">
                    <h3 style="color:var(--danger);">❌ Не найдена</h3>
                    <p>Трек "${track}" отсутствует в системе</p>
                </div>
            `;
        }
    } catch (error) {
        resultsDiv.innerHTML = '<div style="color:var(--danger);text-align:center;">⚠️ Ошибка соединения</div>';
    }
}