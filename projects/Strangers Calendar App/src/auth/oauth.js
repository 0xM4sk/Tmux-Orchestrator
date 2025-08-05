|
const express = require('express');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const AppleStrategy = require('passport-apple-oauth2').Strategy;

const router = express.Router();

// Google OAuth Strategy
passport.use(new GoogleStrategy({
clientID: 'your_google_client_id',
clientSecret: 'your_google_client_secret',
callbackURL: '/auth/google/callback'
},
function(accessToken, refreshToken, profile, cb) {
return cb(null, profile);
}
));

// Apple OAuth Strategy
passport.use(new AppleStrategy({
clientID: 'your_apple_client_id',
teamID: 'your_team_id',
callbackURL: '/auth/apple/callback'
},
function(accessToken, refreshToken, profile, cb) {
return cb(null, profile);
}
));

// Google Auth Routes
router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }));
router.get('/google/callback', 
passport.authenticate('google', { failureRedirect: '/login' }),
function(req, res) {
// Successful authentication, redirect home.
res.redirect('/');
});

// Apple Auth Routes
router.get('/apple', passport.authenticate('apple', { scope: ['profile'] }));
router.get('/apple/callback', 
passport.authenticate('apple', { failureRedirect: '/login' }),
function(req, res) {
// Successful authentication, redirect home.
res.redirect('/');
});

module.exports = router;