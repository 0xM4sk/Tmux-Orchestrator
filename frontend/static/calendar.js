|
document.addEventListener('DOMContentLoaded', () => {
fetch('/api/calendars')
.then(response => response.json())
.then(data => {
const calendarDiv = document.getElementById('calendar');
data.forEach(calendar => {
const div = document.createElement('div');
div.innerHTML = `<h2>${calendar.name}</h2><p>Events: ${calendar.events.length}</p>`;
calendarDiv.appendChild(div);
});
})
.catch(error => console.error('Error fetching calendars:', error));
});