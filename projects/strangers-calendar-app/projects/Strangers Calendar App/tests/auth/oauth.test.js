|
const test = require('ava');
const app = require('../src/auth/oauth');

test('get_google_auth_url should return correct URL', (t) => {
t.is(app.get_google_auth_url(), 'https://accounts.google.com/o/oauth2/auth');
});

test('get_apple_auth_url should return correct URL', (t) => {
t.is(app.get_apple_auth_url(), 'https://appleid.apple.com/auth/authorize');
});