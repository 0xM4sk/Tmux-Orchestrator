|
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserProfileView = ({ match }) => {
const [profile, setProfile] = useState(null);

useEffect(() => {
const fetchProfile = async () => {
try {
const response = await axios.get(`/api/user_profiles/${match.params.id}`);
setProfile(response.data);
} catch (error) {
console.error(error);
alert('Error fetching profile');
}
};

fetchProfile();
}, [match.params.id]);

if (!profile) return <div>Loading...</div>;

return (
<div>
<h2>User Profile</h2>
<p>Name: {profile.name}</p>
<p>Email: {profile.email}</p>
</div>
);
};

export default UserProfileView;