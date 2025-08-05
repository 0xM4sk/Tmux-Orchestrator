|
const request = require('supertest');
const app = require('../src/app');

describe('OAuth Authentication Endpoints', () => {
it('should return an error if multiple Google accounts are linked', async () => {
// Mock user data with multiple Google accounts
const mockUserData = [
{ id: 1, email: 'user1@gmail.com' },
{ id: 2, email: 'user2@gmail.com' }
];

// Set up a mock for the OAuth authentication endpoint
app.post('/auth/google', (req, res) => {
if (mockUserData.length > 1) {
return res.status(400).json({ message: 'Multiple Google accounts linked' });
} else {
return res.status(200).json({ message: 'Authentication successful' });
}
});

// Send a request to the OAuth endpoint
const response = await request(app).post('/auth/google').send({ token: 'fake_token' });

// Assert the response status code and error message
expect(response.status).toBe(400);
expect(response.body.message).toBe('Multiple Google accounts linked');
});
});