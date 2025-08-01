|
import express from 'express';
import request from 'supertest';
import MockOAuth from '../mocks/oauthService';

const app = express();
// Import your OAuth routes here
// Example:
// import { googleAuth } from '../routes/authRoutes';
// app.use('/auth/google', googleAuth);

describe('Google Authentication Endpoint', () => {
beforeEach(() => {
MockOAuth.authenticate.mockClear();
});

it('should authenticate user with Google and return a token', async () => {
const res = await request(app)
.post('/auth/google')
.send({ id_token: 'google-id-token' });

expect(res.status).toBe(200);
expect(MockOAuth.authenticate).toHaveBeenCalledWith({ id_token: 'google-id-token' });
});

it('should handle authentication error', async () => {
MockOAuth.authenticate.mockRejectedValue(new Error('Invalid ID token'));

const res = await request(app)
.post('/auth/google')
.send({ id_token: 'google-id-token' });

expect(res.status).toBe(401);
expect(MockOAuth.authenticate).toHaveBeenCalledWith({ id_token: 'google-id-token' });
});
});