|
const request = require('supertest');
const app = require('../app');
const AppleOAuthRouter = require('../backend/auth/routes_apple_oauth');

describe('Apple OAuth Routes', () => {
it('should redirect to Apple auth URL', async () => {
await request(app)
.get('/api/auth/apple')
.expect(302);
});

it('should handle Apple callback route', async () => {
await request(app)
.get('/api/auth/apple/callback')
.expect(302);
});
});