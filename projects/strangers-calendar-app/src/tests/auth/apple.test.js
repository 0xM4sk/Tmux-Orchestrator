|
const request = require('supertest');
const app = require('../server');

describe('Apple OAuth Authentication', () => {
it('should redirect to Apple login page', async () => {
const response = await request(app).get('/api/auth/apple/login');
expect(response.status).toBe(302);
expect(response.headers.location).toContain('appleid.apple.com');
});

it('should handle authentication callback successfully', async () => {
// Mock the authentication logic
jest.spyOn(passport, 'authenticate').mockImplementation((strategy, options, callback) => (req, res) => {
req.user = { id: 1, username: 'testuser' };
return callback(null, true);
});

const response = await request(app).get('/api/auth/apple/callback')
.set('Cookie', ['connect.sid=s%3Aabcde.12345']);

expect(response.status).toBe(302);
expect(response.headers.location).toBe('/');
});
});