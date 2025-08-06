|
import React from 'react';
import axios from 'axios';

const DeleteEvent = ({ eventId }) => {
const handleDelete = async () => {
try {
await axios.delete(`/api/events/${eventId}`);
alert('Event deleted successfully!');
} catch (error) {
console.error(error);
alert('Error deleting event');
}
};

return (
<button onClick={handleDelete}>Delete Event</button>
);
};

export default DeleteEvent;