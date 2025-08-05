|
// Unit test for OAuth routes
const request = require('supertest');
const app = require('../../app'); // Adjust the path to your main app file

describe('OAuth Routes', () => {
it('should redirect to Google login page', async () => {
const response = await request(app).get('/auth/google').expect(302);
expect(response.header.location).toBe('/login');
});

it('should handle Google callback route', async () => {
const response = await request(app)
.get('/auth/google/callback')
.query({ code: 'fake_code' })
.expect(302);
expect(response.header.location).toBe('/');
});

it('should redirect to Apple login page', async () => {
const response = await request(app).get('/auth/apple').expect(302);
expect(response.header.location).toBe('/login');
});

it('should handle Apple callback route', async () => {
const response = await request(app)
.get('/auth/apple/callback')
.query({ code: 'fake_code' })
.expect(302);
expect(response.header.location).toBe('/');
});
});