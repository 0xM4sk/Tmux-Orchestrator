|
import React, { useState } from 'react';
import axios from 'axios';

const UpdateEvent = ({ eventId }) => {
const [title, setTitle] = useState('');
const [description, setDescription] = useState('');

const handleSubmit = async (e) => {
e.preventDefault();
try {
await axios.put(`/api/events/${eventId}`, { title, description });
alert('Event updated successfully!');
} catch (error) {
console.error(error);
alert('Error updating event');
}
};

return (
<form onSubmit={handleSubmit}>
<input
type="text"
placeholder="Title"
value={title}
onChange={(e) => setTitle(e.target.value)}
/>
<textarea
placeholder="Description"
value={description}
onChange={(e) => setDescription(e.target.value)}
/>
<button type="submit">Update Event</button>
</form>
);
};

export default UpdateEvent;