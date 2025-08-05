|
import React from 'react';
import { useHistory } from 'react-router-dom';

const OAuthLogin = () => {
const history = useHistory();

const handleGoogleLogin = () => {
window.location.href = '/login';
};

return (
<div>
<h1>Login with OAuth</h1>
<button onClick={handleGoogleLogin}>Login with Google</button>
</div>
);
};

export default OAuthLogin;