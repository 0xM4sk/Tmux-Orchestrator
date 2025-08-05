|
const userService = require('../../services/user_service');
const mailServiceMock = {
sendEmail: jest.fn()
};

beforeEach(() => {
jest.mock('../../services/mail_service', () => ({
getInstance: () => mailServiceMock
}));
});

test('sendRegistrationEmail should call mailService.sendEmail with correct parameters', async () => {
const user = { email: 'test@example.com' };
await userService.sendRegistrationEmail(user);
expect(mailServiceMock.sendEmail).toHaveBeenCalledWith(user.email, 'Welcome to Strangers Calendar App', expect.any(String));
});