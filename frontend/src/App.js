|
import React, { useState } from 'react';
import PhoneNumberInput from './components/PhoneNumberInput';

const App = () => {
const [phoneNumber, setPhoneNumber] = useState('');

const handlePhoneNumberSubmit = (number) => {
setPhoneNumber(number);
console.log('Phone number:', number);
};

return (
<div>
<h1>Phone Number Input and Validation</h1>
<PhoneNumberInput onSubmit={handlePhoneNumberSubmit} />
{phoneNumber && <p>Submitted Phone Number: {phoneNumber}</p>}
</div>
);
};

export default App;