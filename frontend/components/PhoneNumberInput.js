|
import React from 'react';
import './forms.css';

const PhoneNumberInput = ({ onChange }) => {
return (
<div className="form-group">
<label htmlFor="phoneNumber">Phone Number</label>
<input
type="tel"
id="phoneNumber"
name="phoneNumber"
pattern="[0-9]{10}"
required
onChange={onChange}
placeholder="Enter your phone number"
className="form-control"
/>
</div>
);
};

export default PhoneNumberInput;