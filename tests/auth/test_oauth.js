|
const express = require('express');
const app = express();
const { get_google_auth_url } = require('../src/auth');

describe('get_google_auth_url', () => {
it('should generate the correct URL', () => {
const url = get_google_auth_url('client_id', 'redirect_uri', 'scope');
expect(url).toBe('https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=client_id&redirect_uri=redirect_uri&scope=scope&access_type=offline&approval_prompt=force');
});
});

app.listen(3000, () => {
console.log('Server is running on port 3000');
});