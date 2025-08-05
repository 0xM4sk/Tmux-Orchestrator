|
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserProfileView = ({ userId }) => {
const [userProfile, setUserProfile] = useState(null);

useEffect(() => {
axios.get(`/user_profiles/${userId}`)
.then(response => setUserProfile(response.data))
.catch(error => console.error('Error:', error));
}, [userId]);

if (!userProfile) return <div>Loading...</div>;

return (
<div>
<h1>User Profile</h1>
<p>Username: {userProfile.username}</p>
<p>Email: {userProfile.email}</p>
</div>
);
};

export default UserProfileView;