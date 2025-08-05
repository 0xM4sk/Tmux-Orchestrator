|
// Service for recurring events
const RecurringEventModel = require('../models/RecurringEvent');

exports.createRecurringEvent = async (eventData) => {
const newEvent = new RecurringEventModel(eventData);
await newEvent.save();
return newEvent;
};

exports.getAllRecurringEvents = async () => {
const events = await RecurringEventModel.find();
return events;
};