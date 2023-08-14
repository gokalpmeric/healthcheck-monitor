function loadMonitors() {
    fetch('/monitors')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('monitorTable').querySelector('tbody');
            tableBody.innerHTML = '';
            data.forEach((monitor, index) => {
                const row = tableBody.insertRow();
                row.insertCell().innerText = monitor.url; // Display URL
                const statusCell = row.insertCell();
                const statusCircle = document.createElement('div');
                statusCircle.className = `status-circle status-${monitor.status}`;
                statusCell.appendChild(statusCircle);
                const statusText = document.createTextNode(` ${monitor.status}`); // Add space to separate the circle and text
                statusCell.appendChild(statusText);
                const deleteButton = document.createElement('button');
                deleteButton.innerText = 'Delete';
                deleteButton.className = 'btn btn-danger';
                deleteButton.onclick = () => deleteMonitor(index);
                row.insertCell().appendChild(deleteButton);
            });
        });
}

function deleteMonitor(index) {
    fetch(`/monitors/${index}`, {
        method: 'DELETE'
    })
    .then(() => {
        loadMonitors();
    });
}

document.getElementById('addMonitorForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const url = document.getElementById('url').value;
    fetch('/monitors', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            url: url
        })
    })
    .then(() => {
        document.getElementById('url').value = '';
        loadMonitors();
    });
});

function updateCounter() {
    const counterElement = document.querySelector('.counter');
    let counterValue = parseInt(counterElement.innerText);

    if (counterValue > 0) {
        counterElement.innerText = (counterValue - 1).toString();
    } else {
        counterElement.innerText = "59";
        loadMonitors();
        document.querySelector('.last-updated').innerText = new Date().toLocaleTimeString();
    }
}

// Call updateCounter every second
setInterval(updateCounter, 1000);

// Initial load of monitors
loadMonitors();
