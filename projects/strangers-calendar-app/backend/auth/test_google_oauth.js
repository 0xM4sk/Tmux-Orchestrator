|
const request = require('supertest');
const app = require('../app');
const GoogleOAuthRouter = require('../backend/auth/routes_google_oauth');

describe('Google OAuth Routes', () => {
it('should redirect to Google auth URL', async () => {
await request(app)
.get('/api/auth/google')
.expect(302);
});

it('should handle Google callback route', async () => {
await request(app)
.get('/api/auth/google/callback')
.expect(302);
});
});