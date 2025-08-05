|
// Google OAuth authentication implementation
const express = require('express');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;

const googleClientID = 'your_google_client_id';
const googleClientSecret = 'your_google_client_secret';

passport.use(new GoogleStrategy({
clientID: googleClientID,
clientSecret: googleClientSecret,
callbackURL: "http://localhost:3000/auth/google/callback"
},
function(accessToken, refreshToken, profile, cb) {
// User model logic here to save or update user
return cb(null, profile);
}
));

passport.serializeUser(function(user, done) {
done(null, user);
});

passport.deserializeUser(function(user, done) {
done(null, user);
});

const router = express.Router();

router.get('/google',
passport.authenticate('google', { scope: ['profile'] }));

router.get('/google/callback', 
passport.authenticate('google', { failureRedirect: '/login' }),
function(req, res) {
// Successful authentication, redirect home.
res.redirect('/');
});

module.exports = router;