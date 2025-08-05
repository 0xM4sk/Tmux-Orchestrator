|
// Phone Input component

import React, { useState } from 'react';
import axios from 'axios';

const PhoneInput = () => {
const [phoneNumber, setPhoneNumber] = useState('');
const [error, setError] = useState('');
const [successMessage, setSuccessMessage] = useState('');

const handleSubmit = async (e) => {
e.preventDefault();

try {
const response = await axios.post('/validate_phone', { phone_number: phoneNumber });
if (response.data.status === 'success') {
setSuccessMessage(response.data.message);
setError('');
} else {
setError(response.data.message);
setSuccessMessage('');
}
} catch (error) {
setError('An error occurred. Please try again later.');
setSuccessMessage('');
}
};

return (
<div>
<form onSubmit={handleSubmit}>
<label htmlFor="phone_number">Phone Number:</label>
<input
type="text"
id="phone_number"
value={phoneNumber}
onChange={(e) => setPhoneNumber(e.target.value)}
required
/>
<button type="submit">Submit</button>
</form>

{error && <p style={{ color: 'red' }}>{error}</p>}
{successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
</div>
);
};

export default PhoneInput;