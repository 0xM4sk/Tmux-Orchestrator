|
const auth = require('../src/auth/oauth');

describe('Test get_google_auth_url', () => {
it('should return a valid URL string', () => {
const url = auth.get_google_auth_url();
expect(url).toBeInstanceOf(String);
expect(url.startsWith('https://accounts.google.com/o/oauth2/auth')).toBe(true);
});
});