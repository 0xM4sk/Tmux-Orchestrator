|
import React, { useState } from 'react';

const UserProfileForm = () => {
const [username, setUsername] = useState('');
const [email, setEmail] = useState('');
const [passwordHash, setPasswordHash] = useState('');

const handleSubmit = (e) => {
e.preventDefault();
fetch('/user_profiles', {
method: 'POST',
headers: {
'Content-Type': 'application/json'
},
body: JSON.stringify({ username, email, passwordHash })
}).then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
};

return (
<form onSubmit={handleSubmit}>
<input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
<input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
<input type="password" placeholder="Password" value={passwordHash} onChange={(e) => setPasswordHash(e.target.value)} />
<button type="submit">Create User Profile</button>
</form>
);
};

export default UserProfileForm;