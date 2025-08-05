|
// OAuth authentication implementation
const express = require('express');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const AppleStrategy = require('passport-apple').AppleStrategy;

const router = express.Router();

// Configure Google Strategy
passport.use(new GoogleStrategy({
clientID: process.env.GOOGLE_CLIENT_ID,
clientSecret: process.env.GOOGLE_CLIENT_SECRET,
callbackURL: "/auth/google/callback"
},
function(accessToken, refreshToken, profile, cb) {
User.findOrCreate({ googleId: profile.id }, function (err, user) {
return cb(err, user);
});
}
));

// Configure Apple Strategy
passport.use(new AppleStrategy({
clientID: process.env.APPLE_CLIENT_ID,
teamID: process.env.APPLE_TEAM_ID,
keyID: process.env.APPLE_KEY_ID,
privateKey: require('fs').readFileSync('/path/to/private-key.p8'),
callbackURL: "/auth/apple/callback"
},
function(accessToken, refreshToken, profile, cb) {
User.findOrCreate({ appleId: profile.id }, function (err, user) {
return cb(err, user);
});
}
));

// Google Authentication Routes
router.get('/google',
passport.authenticate('google', { scope: ['profile'] }));

router.get('/google/callback', 
passport.authenticate('google', { failureRedirect: '/login' }),
function(req, res) {
// Successful authentication, redirect home.
res.redirect('/');
});

// Apple Authentication Routes
router.get('/apple',
passport.authenticate('apple'));

router.get('/apple/callback', 
passport.authenticate('apple', { failureRedirect: '/login' }),
function(req, res) {
// Successful authentication, redirect home.
res.redirect('/');
});

module.exports = router;