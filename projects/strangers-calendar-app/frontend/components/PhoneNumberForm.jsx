|
import React, { useState } from 'react';

const PhoneNumberForm = ({ onSubmit }) => {
const [phoneNumber, setPhoneNumber] = useState('');
const [error, setError] = useState(null);

const handleSubmit = (e) => {
e.preventDefault();
if (!validatePhoneNumber(phoneNumber)) {
setError('Please enter a valid phone number.');
return;
}
setError(null);
onSubmit(phoneNumber);
};

const validatePhoneNumber = (number) => {
// Simple regex to check for valid US phone numbers
const regex = /^\d{10}$/;
return regex.test(number);
};

return (
<form onSubmit={handleSubmit}>
<div>
<label htmlFor="phoneNumber">Phone Number:</label>
<input
type="text"
id="phoneNumber"
value={phoneNumber}
onChange={(e) => setPhoneNumber(e.target.value)}
/>
</div>
{error && <p style={{ color: 'red' }}>{error}</p>}
<button type="submit">Submit</button>
</form>
);
};

export default PhoneNumberForm;