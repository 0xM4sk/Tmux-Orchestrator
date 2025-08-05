|
// Google OAuth configuration
module.exports = {
clientID: process.env.GOOGLE_CLIENT_ID,
clientSecret: process.env.GOOGLE_CLIENT_SECRET,
callbackURL: 'http://localhost:3001/auth/google/callback'
};