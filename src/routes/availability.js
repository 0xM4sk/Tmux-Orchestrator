|
const express = require('express');
const router = express.Router();
const AvailabilityWindow = require('../models/AvailabilityWindow');

// Create a new availability window
router.post('/availability', async (req, res) => {
try {
const { userId, startTime, endTime } = req.body;
const availabilityWindow = new AvailabilityWindow({ userId, startTime, endTime });
await availabilityWindow.save();
res.status(201).send(availabilityWindow);
} catch (error) {
res.status(500).send(error.message);
}
});

// Get all availability windows for a user
router.get('/availability/:userId', async (req, res) => {
try {
const userId = req.params.userId;
const availabilityWindows = await AvailabilityWindow.find({ userId });
res.send(availabilityWindows);
} catch (error) {
res.status(500).send(error.message);
}
});

// Delete an availability window
router.delete('/availability/:id', async (req, res) => {
try {
const id = req.params.id;
await AvailabilityWindow.findByIdAndDelete(id);
res.status(204).send();
} catch (error) {
res.status(500).send(error.message);
}
});

module.exports = router;