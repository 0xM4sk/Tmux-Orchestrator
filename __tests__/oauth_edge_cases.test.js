|
// Additional test cases for OAuth edge scenarios
const { authenticateWithGoogle, authenticateWithApple } = require('../src/auth/oauth');
const { expect } = require('@jest/globals');

describe('OAuth Edge Cases', () => {
it('Test OAuth authentication with invalid credentials', async () => {
await expect(authenticateWithGoogle({ email: 'invalid@example.com', password: 'invalid' })).rejects.toThrowError('Invalid credentials');
await expect(authenticateWithApple({ email: 'invalid@example.com', password: 'invalid' })).rejects.toThrowError('Invalid credentials');
});

it('Test OAuth authentication flow with different user roles (admin)', async () => {
const authAdmin = authenticateWithGoogle({ email: 'admin@example.com', password: 'password123' });
await expect(authAdmin).resolves.toMatchObject({ role: 'admin' });
});

it('Test OAuth authentication flow with different user roles (regular user)', async () => {
const authUser = authenticateWithApple({ email: 'user@example.com', password: 'password123' });
await expect(authUser).resolves.toMatchObject({ role: 'user' });
});
});