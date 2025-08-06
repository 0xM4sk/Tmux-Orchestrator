|
import React, { useState } from 'react';
import axios from 'axios';

const SearchEvent = () => {
const [query, setQuery] = useState('');
const [events, setEvents] = useState([]);
const [filteredEvents, setFilteredEvents] = useState([]);

const handleSearchChange = (event) => {
setQuery(event.target.value);
if (event.target.value.trim() === '') {
setFilteredEvents(events);
} else {
const filtered = events.filter(event =>
event.title.toLowerCase().includes(event.target.value.toLowerCase())
);
setFilteredEvents(filtered);
}
};

const fetchEvents = async () => {
try {
const response = await axios.get('/api/events');
setEvents(response.data);
setFilteredEvents(response.data);
} catch (error) {
console.error('Error fetching events:', error);
}
};

useEffect(() => {
fetchEvents();
}, []);

return (
<div>
<input
type="text"
placeholder="Search events..."
value={query}
onChange={handleSearchChange}
/>
<ul>
{filteredEvents.map(event => (
<li key={event.id}>{event.title}</li>
))}
</ul>
</div>
);
};

export default SearchEvent;