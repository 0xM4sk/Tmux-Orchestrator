|
// Auth Routes
const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

router.get('/google', authController.loginGoogle);
router.get('/google/callback', (req, res) => {
// Handle the callback here
res.send('Google OAuth Callback');
});

module.exports = router;