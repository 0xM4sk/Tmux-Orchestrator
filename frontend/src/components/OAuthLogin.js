|
import React from 'react';
import { GoogleLogin, AppleLogin } from 'react-google-login';

const OAuthLoginComponent = () => {
const onSuccessGoogle = (res) => {
console.log('Success:', res);
// Handle successful login
};

const onFailureGoogle = (err) => {
console.error('Failure:', err);
};

const onSuccessApple = (res) => {
console.log('Success:', res);
// Handle successful login
};

const onFailureApple = (err) => {
console.error('Failure:', err);
};

return (
<div>
<GoogleLogin
clientId="your_google_client_id"
buttonText="Login with Google"
onSuccess={onSuccessGoogle}
onFailure={onFailureGoogle}
/>
<AppleLogin
clientId="your_apple_client_id"
redirectURI="http://localhost:3000/callback"
onSuccess={onSuccessApple}
onError={onFailureApple}
/>
</div>
);
};

export default OAuthLoginComponent;