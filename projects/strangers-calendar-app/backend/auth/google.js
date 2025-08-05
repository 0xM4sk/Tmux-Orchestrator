|
// Google OAuth configuration
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;

module.exports = function (passport) {
passport.use(new GoogleStrategy({
clientID: 'GOOGLE_CLIENT_ID',
clientSecret: 'GOOGLE_CLIENT_SECRET',
callbackURL: "/auth/google/callback"
},
function(accessToken, refreshToken, profile, cb) {
// User creation or retrieval logic here
return cb(null, profile);
}
));
};