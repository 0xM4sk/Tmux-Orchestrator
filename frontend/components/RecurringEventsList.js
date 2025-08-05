|
// Component to display recurring event occurrences
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const RecurringEventsList = () => {
const [events, setEvents] = useState([]);

useEffect(() => {
axios.get('/api/recurring-events')
.then(response => setEvents(response.data))
.catch(error => console.error('Error fetching recurring events:', error));
}, []);

return (
<ul>
{events.map(event => (
<li key={event.id}>
{event.eventName} - {event.startTime} to {event.endTime}
</li>
))}
</ul>
);
};

export default RecurringEventsList;