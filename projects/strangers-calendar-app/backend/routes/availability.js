|
const express = require('express');
const router = express.Router();
const availabilityController = require('../controllers/availabilityController');

// POST /api/availability - Add an availability window and calculate intersections
router.post('/', availabilityController.addAvailability);

module.exports = router;