|
import React, { useState } from 'react';

const PhoneNumberInput = ({ onSubmit }) => {
const [phoneNumber, setPhoneNumber] = useState('');
const [error, setError] = useState('');

const handleSubmit = (e) => {
e.preventDefault();
if (!/^\+?\d{10,15}$/.test(phoneNumber)) {
setError('Invalid phone number');
} else {
onSubmit(phoneNumber);
setPhoneNumber('');
setError('');
}
};

return (
<form onSubmit={handleSubmit}>
<label>
Phone Number:
<input
type="text"
value={phoneNumber}
onChange={(e) => setPhoneNumber(e.target.value)}
/>
</label>
{error && <p style={{ color: 'red' }}>{error}</p>}
<button type="submit">Submit</button>
</form>
);
};

export default PhoneNumberInput;