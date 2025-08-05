|
const express = require('express');
const router = express.Router();
const TemporaryCalendar = require('../models/TemporaryCalendar');

// Create a temporary calendar
router.post('/', async (req, res) => {
try {
const temporaryCalendar = new TemporaryCalendar(req.body);
await temporaryCalendar.save();
res.status(201).json(temporaryCalendar);
} catch (error) {
res.status(500).json({ message: error.message });
}
});

module.exports = router;