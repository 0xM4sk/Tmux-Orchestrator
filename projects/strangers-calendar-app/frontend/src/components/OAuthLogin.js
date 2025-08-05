|
// OAuth login component for Google and Apple
import React from 'react';
import { useGoogleOAuth, useAppleOAuth } from '../hooks/useOauth';

const OAuthLogin = () => {
const googleLogin = useGoogleOAuth();
const appleLogin = useAppleOAuth();

return (
<div>
<button onClick={googleLogin}>Login with Google</button>
<button onClick={appleLogin}>Login with Apple</button>
</div>
);
};

export default OAuthLogin;