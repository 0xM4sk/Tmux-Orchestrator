|
const Availability = require('../models/Availability');

exports.addAvailability = async (req, res) => {
try {
const { startTime, endTime } = req.body;
const availability = new Availability({ startTime, endTime });
await availability.save();
res.status(201).json(availability);
} catch (error) {
res.status(400).json({ error: 'Invalid data' });
}
};