|
const express = require('express');
const request = require('supertest');
const app = require('../../src/index');

describe('OAuth Authentication Endpoints', () => {
it('should return 401 for invalid client ID/secret', async () => {
const response = await request(app)
.post('/auth/oauth/token')
.send({
grant_type: 'client_credentials',
client_id: 'invalid-client-id',
client_secret: 'invalid-client-secret'
});

expect(response.status).toBe(401);
});

it('should return 400 for expired access token', async () => {
const response = await request(app)
.post('/auth/oauth/token')
.send({
grant_type: 'client_credentials',
client_id: 'valid-client-id',
client_secret: 'valid-client-secret'
});

expect(response.status).toBe(400);
});

it('should return 400 for invalid grant type', async () => {
const response = await request(app)
.post('/auth/oauth/token')
.send({
grant_type: 'invalid-grant-type',
client_id: 'valid-client-id',
client_secret: 'valid-client-secret'
});

expect(response.status).toBe(400);
});

it('should return 400 for missing required parameters', async () => {
const response = await request(app)
.post('/auth/oauth/token')
.send({
grant_type: 'client_credentials',
client_id: 'valid-client-id'
});

expect(response.status).toBe(400);
});
});