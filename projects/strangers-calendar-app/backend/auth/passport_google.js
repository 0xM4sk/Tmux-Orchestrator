|
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const keys = require('../config/keys');

passport.use(new GoogleStrategy({
clientID: keys.googleClientID,
clientSecret: keys.googleClientSecret,
callbackURL: '/api/auth/google/callback'
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