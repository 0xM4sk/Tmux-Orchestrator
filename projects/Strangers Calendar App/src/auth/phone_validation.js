|
// Phone number input and validation logic
const Joi = require('joi');

const phoneNumberSchema = Joi.string()
.pattern(/^\+1\d{10}$/)
.messages({
'string.pattern.base': 'Phone number must be in the format +1XXXXXXXXXX'
});

function validatePhoneNumber(phoneNumber) {
return phoneNumberSchema.validate(phoneNumber);
}

module.exports = { validatePhoneNumber };