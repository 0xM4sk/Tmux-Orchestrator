|
// Auth Controller
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const googleConfig = require('../config/google');

passport.use(new GoogleStrategy({
clientID: googleConfig.clientID,
clientSecret: googleConfig.clientSecret,
callbackURL: googleConfig.callbackURL
}, (accessToken, refreshToken, profile, cb) => {
// Handle the user here
return cb(null, profile);
}));

module.exports = {
loginGoogle: passport.authenticate('google', { scope: ['profile'] })
};