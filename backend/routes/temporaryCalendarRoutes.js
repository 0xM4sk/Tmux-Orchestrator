|
const express = require('express');
const router = express.Router();
const temporaryCalendarController = require('../controllers/temporaryCalendarController');

// Get all temporary calendars
router.get('/', temporaryCalendarController.getAllTemporaryCalendars);

module.exports = router;