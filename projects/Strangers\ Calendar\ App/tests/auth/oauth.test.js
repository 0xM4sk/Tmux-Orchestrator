|
const express = require('express');
const request = require('supertest');
const app = express();
const oauthRouter = require('../src/auth/oauth');

app.use('/', oauthRouter);

describe('OAuth Authentication', () => {
it('should redirect to Google authentication page', async () => {
const response = await request(app)
.get('/auth/google')
.expect(302);
expect(response.headers.location).toContain('/oauth2/authorization/google');
});

it('should redirect to Apple authentication page', async () => {
const response = await request(app)
.get('/auth/apple')
.expect(302);
expect(response.headers.location).toContain('/auth.apple.com/');
});
});