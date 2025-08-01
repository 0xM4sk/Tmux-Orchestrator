|
// OAuth authentication implementation
const express = require('express');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const AppleStrategy = require('passport-apple').Strategy;

const app = express();

// Passport configuration
passport.use(new GoogleStrategy({
clientID: 'your_google_client_id',
clientSecret: 'your_google_client_secret',
callbackURL: '/auth/google/callback'
},
function(accessToken, refreshToken, profile, cb) {
return cb(null, profile);
}
));

passport.use(new AppleStrategy({
clientID: 'your_apple_client_id',
teamID: 'your_team_id',
keyID: 'your_key_id',
privateKeyPath: '/path/to/private/key.p8'
},
function(accessToken, refreshToken, profile, cb) {
return cb(null, profile);
}
));

app.use(passport.initialize());
app.use(passport.session());

// Routes
app.get('/auth/google', passport.authenticate('google'));
app.get('/auth/google/callback',
passport.authenticate('google', { failureRedirect: '/login' }),
function(req, res) {
// Successful authentication, redirect home.
res.redirect('/');
});

module.exports = app;