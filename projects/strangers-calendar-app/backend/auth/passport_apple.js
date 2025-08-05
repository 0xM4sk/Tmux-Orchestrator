|
const passport = require('passport');
const AppleStrategy = require('passport-apple').Strategy;
const keys = require('../config/keys');

passport.use(new AppleStrategy({
clientID: keys.appleClientID,
teamID: keys.appleTeamID,
callbackURL: '/api/auth/apple/callback',
keyID: keys.appleKeyID,
privateKey: require('fs').readFileSync(keys.applePrivateKeyPath)
},
(accessToken, refreshToken, profile, done) => {
// Save user to database
done(null, profile);
}
));

passport.serializeUser((user, done) => {
done(null, user.id);
});

passport.deserializeUser((id, done) => {
User.findById(id).then(user => done(null, user));
});