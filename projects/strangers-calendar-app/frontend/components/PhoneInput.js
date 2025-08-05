|
import React, { useState } from 'react';

const PhoneInput = () => {
const [phoneNumber, setPhoneNumber] = useState('');
const [error, setError] = useState('');

const handleInputChange = (e) => {
const value = e.target.value;
if (/^\d{10}$/.test(value)) {
setError('');
} else {
setError('Please enter a valid 10-digit phone number.');
}
setPhoneNumber(value);
};

return (
<div>
<input
type="text"
value={phoneNumber}
onChange={handleInputChange}
placeholder="Phone Number"
/>
{error && <p style={{ color: 'red' }}>{error}</p>}
</div>
);
};

export default PhoneInput;