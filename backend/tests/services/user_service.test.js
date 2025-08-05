|
const { sendRegistrationEmail } = require('../../services/userService');
const MailService = require('../../tests/mock/mailService');

beforeAll(() => {
MailService.transporter.sendMail.mockResolvedValue({});
});

describe('User Service', () => {
it('should send registration email successfully', async () => {
const user = { email: 'test@example.com' };
await sendRegistrationEmail(user);
expect(MailService.transporter.sendMail).toHaveBeenCalledWith({
from: 'test@example.com',
to: 'test@example.com',
subject: 'Welcome to Our Service',
text: 'Thank you for registering!'
});
});

it('should handle email sending failure', async () => {
MailService.transporter.sendMail.mockRejectedValue(new Error('Failed to send email'));
const user = { email: 'invalid@example.com' };
try {
await sendRegistrationEmail(user);
fail('Expected an error to be thrown');
} catch (error) {
expect(error.message).toBe('Failed to send email');
}
});
});