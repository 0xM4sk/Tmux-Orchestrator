|
const express = require('express');
const router = express.Router();
const passport = require('../passport');

// Route to initiate Google OAuth
router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

// Callback route for Google OAuth
router.get('/google/callback', 
passport.authenticate('google', {
successRedirect: '/dashboard',
failureRedirect: '/login'
})
);

module.exports = router;