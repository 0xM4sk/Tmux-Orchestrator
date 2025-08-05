|
const express = require('express');
const router = express.Router();
const passport = require('../passport');

// Route to initiate Apple OAuth
router.get('/apple', passport.authenticate('apple'));

// Callback route for Apple OAuth
router.get('/apple/callback', 
passport.authenticate('apple', {
successRedirect: '/dashboard',
failureRedirect: '/login'
})
);

module.exports = router;