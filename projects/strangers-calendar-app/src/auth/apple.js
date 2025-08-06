|
// Apple OAuth authentication implementation
const express = require('express');
const router = express.Router();
const passport = require('passport');
const appleStrategy = require('passport-apple-oauth2').Strategy;

// Configure the Apple strategy for Passport.js
passport.use(new appleStrategy({
clientID: process.env.APPLE_CLIENT_ID,
redirectURI: process.env.APPLE_REDIRECT_URI,
callbackURL: process.env.APPLE_CALLBACK_URL,
stateStore: require('passport-apple-oauth2').defaultStateStore()
},
(accessToken, refreshToken, extraParams, profile, done) => {
// This is where you would typically find or create a user in your database
return done(null, profile);
}
));

// Define routes for Apple OAuth
router.get('/login', passport.authenticate('apple'));
router.get('/callback', 
passport.authenticate('apple', { failureRedirect: '/login' }),
(req, res) => {
// Successful authentication, redirect home.
res.redirect('/');
});

module.exports = router;