|
// Login component with OAuth buttons
import React from 'react';

const Login = () => {
return (
<div>
<button onClick={() => handleGoogleOAuth()}>Login with Google</button>
<button onClick={() => handleAppleOAuth()}>Login with Apple</button>
</div>
);
};

export default Login;