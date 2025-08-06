|
// Apple OAuth authentication implementation
const express = require('express');
const router = express.Router();
const passport = require('passport');

// Apple OAuth login route
router.get('/login', passport.authenticate('apple', { scope: ['email', 'name'] }));

// Apple OAuth callback route
router.get('/callback', 
passport.authenticate('apple', { failureRedirect: '/login' }),
(req, res) => {
// Successful authentication, redirect home.
res.redirect('/');
}
);

module.exports = router;