|
// Controller for recurring events
const RecurringEventService = require('../services/recurringEvents');

exports.createRecurringEvent = async (req, res) => {
try {
const eventData = req.body;
const newEvent = await RecurringEventService.createRecurringEvent(eventData);
res.status(201).json(newEvent);
} catch (error) {
res.status(500).json({ error: 'Failed to create recurring event' });
}
};

exports.getAllRecurringEvents = async (req, res) => {
try {
const events = await RecurringEventService.getAllRecurringEvents();
res.json(events);
} catch (error) {
res.status(500).json({ error: 'Failed to get recurring events' });
}
};