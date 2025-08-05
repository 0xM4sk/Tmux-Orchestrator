|
// Form component for recurring events
import React, { useState } from 'react';

const RecurringEventForm = ({ onSubmit }) => {
const [eventName, setEventName] = useState('');
const [description, setDescription] = useState('');
const [startTime, setStartTime] = useState('');
const [endTime, setEndTime] = useState('');
const [recurrencePattern, setRecurrencePattern] = useState('');

const handleSubmit = (e) => {
e.preventDefault();
onSubmit({
eventName,
description,
startTime,
endTime,
recurrencePattern,
});
};

return (
<form onSubmit={handleSubmit}>
<div>
<label htmlFor="eventName">Event Name:</label>
<input
type="text"
id="eventName"
value={eventName}
onChange={(e) => setEventName(e.target.value)}
/>
</div>
<div>
<label htmlFor="description">Description:</label>
<textarea
id="description"
value={description}
onChange={(e) => setDescription(e.target.value)}
/>
</div>
<div>
<label htmlFor="startTime">Start Time:</label>
<input
type="datetime-local"
id="startTime"
value={startTime}
onChange={(e) => setStartTime(e.target.value)}
/>
</div>
<div>
<label htmlFor="endTime">End Time:</label>
<input
type="datetime-local"
id="endTime"
value={endTime}
onChange={(e) => setEndTime(e.target.value)}
/>
</div>
<div>
<label htmlFor="recurrencePattern">Recurrence Pattern:</label>
<input
type="text"
id="recurrencePattern"
value={recurrencePattern}
onChange={(e) => setRecurrencePattern(e.target.value)}
/>
</div>
<button type="submit">Add Recurring Event</button>
</form>
);
};

export default RecurringEventForm;