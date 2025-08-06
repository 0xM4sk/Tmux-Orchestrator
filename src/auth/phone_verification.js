|
// Phone number verification implementation
const twilio = require('twilio');

class PhoneNumberVerification {
constructor(accountSid, authToken) {
this.client = new twilio(accountSid, authToken);
}

async sendVerificationCode(phoneNumber) {
try {
await this.client.messages.create({
body: 'Your verification code is: 123456',
from: '+1234567890', // Twilio number
to: phoneNumber
});
return true;
} catch (error) {
console.error('Error sending verification code:', error);
throw error;
}
}

async verifyCode(phoneNumber, code) {
try {
const verificationCheck = await this.client.verify.v2.services('your_service_sid')
.verificationChecks.create({ to: phoneNumber, code });

if (verificationCheck.status === 'approved') {
return true;
} else {
throw new Error('Verification failed');
}
} catch (error) {
console.error('Error verifying code:', error);
throw error;
}
}
}

module.exports = PhoneNumberVerification;