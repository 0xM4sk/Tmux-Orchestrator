|
const express = require('express');
const app = express();
const request = require('supertest');

describe('OAuth Authentication', () => {
it('should return a 200 status code for Google OAuth endpoint', async () => {
const response = await request(app).get('/auth/google');
expect(response.status).toBe(200);
});

it('should return a 200 status code for Apple OAuth endpoint', async () => {
const response = await request(app).get('/auth/apple');
expect(response.status).toBe(200);
});
});