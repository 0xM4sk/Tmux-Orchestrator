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
recurrencePattern
});
};

return (
<form onSubmit={handleSubmit}>
<input type="text" placeholder="Event Name" value={eventName} onChange={(e) => setEventName(e.target.value)} />
<textarea placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)}></textarea>
<input type="datetime-local" placeholder="Start Time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
<input type="datetime-local" placeholder="End Time" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
<input type="text" placeholder="Recurrence Pattern" value={recurrencePattern} onChange={(e) => setRecurrencePattern(e.target.value)} />
<button type="submit">Create Recurring Event</button>
</form>
);
};

export default RecurringEventForm;