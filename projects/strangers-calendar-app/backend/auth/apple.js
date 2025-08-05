|
// Apple OAuth configuration
const passport = require('passport');
const AppleStrategy = require('passport-apple-oauth20').Strategy;

module.exports = function (passport) {
passport.use(new AppleStrategy({
clientID: 'APPLE_CLIENT_ID',
teamID: 'APPLE_TEAM_ID',
redirectURI: "/auth/apple/callback",
keyID: 'APPLE_KEY_ID',
},
function(accessToken, refreshToken, profile, cb) {
// User creation or retrieval logic here
return cb(null, profile);
}
));
};