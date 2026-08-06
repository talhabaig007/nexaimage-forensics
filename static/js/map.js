// Map initialization and GPS functionality

function initMap(latitude, longitude) {
    const mapDiv = document.getElementById('map');
    if (!mapDiv) return;
    
    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        console.error('Leaflet not loaded');
        return;
    }
    
    // Initialize map
    const map = L.map('map').setView([latitude, longitude], 15);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Add marker
    const marker = L.marker([latitude, longitude]).addTo(map);
    marker.bindPopup(`
        <b>GPS Location</b><br>
        Latitude: ${latitude}<br>
        Longitude: ${longitude}
    `).openPopup();
    
    // Add circle to show accuracy
    L.circle([latitude, longitude], {
        color: '#00ffff',
        fillColor: '#00ffff',
        fillOpacity: 0.2,
        radius: 50
    }).addTo(map);
    
    // Store map instance
    window.currentMap = map;
}