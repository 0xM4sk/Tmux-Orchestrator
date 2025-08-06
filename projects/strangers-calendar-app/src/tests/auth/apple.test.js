|
const request = require('supertest');
const app = require('../src/index');
const appleAuthRoutes = require('../src/auth/apple');

describe('Apple OAuth Authentication', () => {
it('should redirect to Apple login page when accessing /auth/login', async () => {
const response = await request(app)
.get('/auth/login')
.expect(302);
expect(response.headers.location).toContain('apple.com');
});

it('should authenticate and redirect on successful callback', async () => {
// Mock the passport.authenticate middleware
app.use(passport.initialize());
appleAuthRoutes.get('/callback', 
passport.authenticate('apple', { failureRedirect: '/login' }),
(req, res) => {
res.redirect('/');
});

const response = await request(app)
.get('/auth/callback')
.expect(302);
expect(response.headers.location).toBe('/');
});
});