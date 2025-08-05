|
// List component for recurring events
import React from 'react';

const RecurringEventsList = ({ events }) => {
return (
<ul>
{events.map((event, index) => (
<li key={index}>
<h3>{event.eventName}</h3>
<p>{event.description}</p>
<p>Start: {event.startTime}</p>
<p>End: {event.endTime}</p>
<p>Recurrence Pattern: {event.recurrencePattern}</p>
</li>
))}
</ul>
);
};

export default RecurringEventsList;