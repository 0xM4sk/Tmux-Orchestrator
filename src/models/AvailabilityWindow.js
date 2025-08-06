|
const mongoose = require('mongoose');

const availabilitySchema = new mongoose.Schema({
userId: {
type: String,
required: true
},
startTime: {
type: Date,
required: true
},
endTime: {
type: Date,
required: true
}
});

module.exports = mongoose.model('AvailabilityWindow', availabilitySchema);