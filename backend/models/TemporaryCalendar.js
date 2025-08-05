|
const mongoose = require('mongoose');

const temporaryCalendarSchema = new mongoose.Schema({
title: {
type: String,
required: true
},
start: {
type: Date,
required: true
},
end: {
type: Date,
required: true
}
});

const TemporaryCalendar = mongoose.model('TemporaryCalendar', temporaryCalendarSchema);
module.exports = TemporaryCalendar;