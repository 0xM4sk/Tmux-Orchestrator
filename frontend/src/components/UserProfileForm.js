|
import React, { useState } from 'react';
import axios from 'axios';

const UserProfileForm = () => {
const [formData, setFormData] = useState({
name: '',
email: ''
});

const handleChange = (e) => {
setFormData({ ...formData, [e.target.name]: e.target.value });
};

const handleSubmit = async (e) => {
e.preventDefault();
try {
await axios.post('/api/user_profiles', formData);
alert('Profile created successfully');
} catch (error) {
console.error(error);
alert('Error creating profile');
}
};

return (
<form onSubmit={handleSubmit}>
<div>
<label htmlFor="name">Name:</label>
<input type="text" id="name" name="name" value={formData.name} onChange={handleChange} required />
</div>
<div>
<label htmlFor="email">Email:</label>
<input type="email" id="email" name="email" value={formData.email} onChange={handleChange} required />
</div>
<button type="submit">Create Profile</button>
</form>
);
};

export default UserProfileForm;