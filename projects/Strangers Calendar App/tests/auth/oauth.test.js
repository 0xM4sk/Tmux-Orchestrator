|
const express = require('express');
const request = require('supertest');
const oauthRouter = require('../auth/oauth');

describe('OAuth Authentication', () => {
let app;

beforeEach(() => {
app = express();
app.use('/api/oauth', oauthRouter);
});

it('should handle Google OAuth endpoint', async () => {
const response = await request(app).get('/api/oauth/google');
expect(response.status).toBe(200);
// Add more assertions as needed
});

it('should handle Apple OAuth endpoint', async () => {
const response = await request(app).get('/api/oauth/apple');
expect(response.status).toBe(200);
// Add more assertions as needed
});
});