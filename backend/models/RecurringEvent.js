|
// Model for recurring events
const mongoose = require('mongoose');

const RecurringEventSchema = new mongoose.Schema({
eventName: {
type: String,
required: true,
},
description: {
type: String,
},
startTime: {
type: Date,
required: true,
},
endTime: {
type: Date,
required: true,
},
recurrencePattern: {
type: String,
required: true,
},
});

const RecurringEvent = mongoose.model('RecurringEvent', RecurringEventSchema);

module.exports = RecurringEvent;