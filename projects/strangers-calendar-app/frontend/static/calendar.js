|
document.addEventListener('DOMContentLoaded', function() {
fetch('/api/calendars')
.then(response => response.json())
.then(data => {
const calendarContainer = document.getElementById('calendar');
data.forEach(calendar => {
const div = document.createElement('div');
div.innerHTML = `<h2>${calendar.title}</h2><p>Start: ${calendar.start}<br>End: ${calendar.end}</p>`;
calendarContainer.appendChild(div);
});
})
.catch(error => console.error('Error fetching calendars:', error));
});