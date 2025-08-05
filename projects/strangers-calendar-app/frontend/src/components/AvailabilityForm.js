|
import React, { useState } from 'react';
import axios from 'axios';

const AvailabilityForm = () => {
const [startTime, setStartTime] = useState('');
const [endTime, setEndTime] = useState('');

const handleSubmit = async (e) => {
e.preventDefault();
try {
await axios.post('/api/availability', { startTime, endTime });
alert('Availability window added successfully!');
setStartTime('');
setEndTime('');
} catch (error) {
console.error('Error adding availability window:', error);
alert('Failed to add availability window.');
}
};

return (
<form onSubmit={handleSubmit}>
<div>
<label>Start Time:</label>
<input
type="time"
value={startTime}
onChange={(e) => setStartTime(e.target.value)}
required
/>
</div>
<div>
<label>End Time:</label>
<input
type="time"
value={endTime}
onChange={(e) => setEndTime(e.target.value)}
required
/>
</div>
<button type="submit">Add Availability</button>
</form>
);
};

export default AvailabilityForm;