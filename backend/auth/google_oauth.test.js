|
const request = require('supertest');
const express = require('express');
const mongoose = require('mongoose');
const authRoutes = require('./google_oauth');

const app = express();
app.use('/auth', authRoutes);

describe('Google OAuth Authentication', () => {
it('should redirect to Google for authentication', async () => {
const response = await request(app).get('/auth/google');
expect(response.status).toBe(302);
expect(response.headers.location).toContain('https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=');
});

it('should handle Google OAuth callback', async () => {
// Mock the authentication process
const response = await request(app).get('/auth/google/callback');
expect(response.status).toBe(302);
expect(response.headers.location).toContain('/');
});
});