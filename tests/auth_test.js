|
const request = require('supertest');
const app = require('../app'); // Adjust the path as needed

describe('Authentication Endpoints', () => {
test('should return a 200 status code for login endpoint', async () => {
const res = await request(app).post('/login').send({ username: 'test', password: 'password' });
expect(res.statusCode).toBe(200);
});

// Add more tests as needed
});