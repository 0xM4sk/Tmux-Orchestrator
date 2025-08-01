|
const express = require('express');
const router = express.Router();
const OAuth2Server = require('oauth2-server');

const oauth = new OAuth2Server({
model: require('../models/oauthModel'),
accessTokenLifetime: 3600,
allowBearerTokensInQueryString: true
});

router.get('/auth/token', (req, res) => {
return oauth.token()
.then(token => {
res.json({ access_token: token.accessToken });
})
.catch(err => {
res.status(err.code || 500).json({ error: err.name, description: err.message });
});
});

module.exports = router;