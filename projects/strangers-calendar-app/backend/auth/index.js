|
// Passport initialization
const passport = require('passport');
const googleStrategy = require('./google');
const appleStrategy = require('./apple');

module.exports = function (app) {
googleStrategy(passport);
appleStrategy(passport);

app.use(passport.initialize());
app.use(passport.session());

// Serialization and deserialization logic
passport.serializeUser(function(user, done) {
done(null, user);
});

passport.deserializeUser(function(obj, done) {
done(null, obj);
});
};