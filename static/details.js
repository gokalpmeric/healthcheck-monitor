function loadDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const url = urlParams.get('url');
    document.getElementById('monitorUrl').innerText = url;

    fetch(`/monitors/${encodeURIComponent(url)}/daily_data`)
        .then(response => response.json())
        .then(data => {
            const dailyDataDiv = document.getElementById('dailyData');
            dailyDataDiv.innerHTML = '';
            for (const date in data) {
                const dayDiv = document.createElement('div');
                dayDiv.className = 'day';
                const totalMinutes = (data[date]['uptime'] + data[date]['downtime']) / 60;
                const uptimePercentage = (data[date]['uptime'] / (totalMinutes * 60)) * 100;
                dayDiv.innerHTML = `
                    <strong>${date}</strong><br>
                    Uptime: ${uptimePercentage.toFixed(2)}%<br>
                    Uptime: ${Math.floor(data[date]['uptime'] / 60)} minutes<br>
                    Downtime: ${Math.floor(data[date]['downtime'] / 60)} minutes
                `;
                dailyDataDiv.appendChild(dayDiv);
            }
        });
}

loadDetails();
