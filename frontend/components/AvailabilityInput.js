|
import React from 'react';
import './forms.css';

const AvailabilityInput = ({ onChange }) => {
return (
<div className="form-group">
<label htmlFor="availability">Availability</label>
<input
type="text"
id="availability"
name="availability"
required
onChange={onChange}
placeholder="Enter your availability (e.g., 10:00 AM - 2:00 PM)"
className="form-control"
/>
</div>
);
};

export default AvailabilityInput;