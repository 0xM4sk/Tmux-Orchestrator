|
const PhoneNumberVerification = require('../auth/phone_verification');
const twilioMock = jest.mock('twilio');

describe('Phone Number Verification', () => {
let phoneNumberVerification;

beforeEach(() => {
phoneNumberVerification = new PhoneNumberVerification('accountSid', 'authToken');
});

it('sends a verification code', async () => {
const sendVerificationCodeSpy = twilioMock.client.messages.create.mockImplementationOnce(() => Promise.resolve({}));
await phoneNumberVerification.sendVerificationCode('+1234567890');
expect(sendVerificationCodeSpy).toHaveBeenCalledWith({
body: 'Your verification code is: 123456',
from: '+1234567890', // Twilio number
to: '+1234567890'
});
});

it('verifies a valid code', async () => {
const verificationCheckMock = jest.mock('twilio').mockResolvedValueOnce({ status: 'approved' });
await phoneNumberVerification.verifyCode('+1234567890', '123456');
expect(verificationCheckMock).toHaveBeenCalledWith({
to: '+1234567890',
code: '123456'
});
});

it('fails to verify an invalid code', async () => {
const verificationCheckMock = jest.mock('twilio').mockResolvedValueOnce({ status: 'pending' });
await expect(phoneNumberVerification.verifyCode('+1234567890', '123456')).rejects.toThrowError('Verification failed');
});

it('handles Twilio errors', async () => {
const sendVerificationCodeSpy = twilioMock.client.messages.create.mockImplementationOnce(() => Promise.reject(new Error('Twilio error')));
await expect(phoneNumberVerification.sendVerificationCode('+1234567890')).rejects.toThrowError('Twilio error');
});
});