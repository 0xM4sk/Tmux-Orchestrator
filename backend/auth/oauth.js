|
// OAuth authentication implementation
const express = require('express');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const AppleStrategy = require('passport-apple').Strategy;

const router = express.Router();

// Configure Google strategy
passport.use(new GoogleStrategy({
clientID: 'your_google_client_id',
clientSecret: 'your_google_client_secret',
callbackURL: '/auth/google/callback'
},
function(accessToken, refreshToken, profile, cb) {
// Save user profile to database
return cb(null, profile);
}
));

// Configure Apple strategy
passport.use(new AppleStrategy({
clientID: 'your_apple_client_id',
teamID: 'your_team_id',
keyID: 'your_key_id',
privateKey: require('fs').readFileSync('/path/to/private-key.p8'),
callbackURL: '/auth/apple/callback'
},
function(accessToken, refreshToken, profile, cb) {
// Save user profile to database
return cb(null, profile);
}
));

router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

router.get('/google/callback', 
passport.authenticate('google', { failureRedirect: '/login' }),
function(req, res) {
// Successful authentication, redirect home.
res.redirect('/');
});

router.get('/apple', passport.authenticate('apple'));

router.get('/apple/callback', 
passport.authenticate('apple', { failureRedirect: '/login' }),
function(req, res) {
// Successful authentication, redirect home.
res.redirect('/');
});

module.exports = router;