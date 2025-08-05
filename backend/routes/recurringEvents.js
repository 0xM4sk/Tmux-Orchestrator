|
// Routes for recurring events
const express = require('express');
const router = express.Router();
const RecurringEventController = require('../controllers/recurringEvents');

router.post('/', RecurringEventController.createRecurringEvent);
router.get('/', RecurringEventController.getAllRecurringEvents);

module.exports = router;