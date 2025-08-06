|
import React, { useState } from 'react';
import axios from 'axios';

const CreateEvent = () => {
const [title, setTitle] = useState('');
const [description, setDescription] = useState('');

const handleSubmit = async (e) => {
e.preventDefault();
try {
await axios.post('/api/events', { title, description });
alert('Event created successfully!');
} catch (error) {
console.error(error);
alert('Error creating event');
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
<button type="submit">Create Event</button>
</form>
);
};

export default CreateEvent;