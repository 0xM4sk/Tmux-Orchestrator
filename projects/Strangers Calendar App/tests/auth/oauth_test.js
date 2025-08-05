|
// OAuth authentication test cases
const { describe, it, expect } = require('@jest/globals');
const oauthController = require('../src/auth/oauth_controller');

describe('OAuth Authentication', () => {
it('should authenticate with Google', async () => {
const req = { query: { code: 'googleCode' } };
const res = { status: jest.fn(), json: jest.fn() };

await oauthController.googleAuth(req, res);

expect(res.status).toHaveBeenCalledWith(200);
expect(res.json).toHaveBeenCalledWith({ message: 'Authenticated with Google successfully' });
});

it('should authenticate with Apple', async () => {
const req = { query: { code: 'appleCode' } };
const res = { status: jest.fn(), json: jest.fn() };

await oauthController.appleAuth(req, res);

expect(res.status).toHaveBeenCalledWith(200);
expect(res.json).toHaveBeenCalledWith({ message: 'Authenticated with Apple successfully' });
});

// Add more test cases as needed
});