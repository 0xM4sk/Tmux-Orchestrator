|
const express = require('express');
const app = express();
const request = require('supertest');

describe('GET /', () => {
it('responds with "Hello World!"', async () => {
const response = await request(app).get('/');
expect(response.text).toBe('Hello World!');
});
});