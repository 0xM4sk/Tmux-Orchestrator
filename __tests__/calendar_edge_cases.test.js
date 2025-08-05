|
// Additional test cases for calendar edge scenarios
const { Calendar } = require('../src/calendar');
const { expect } = require('@jest/globals');

describe('Calendar Edge Cases', () => {
it('Test calendar creation with large number of users', async () => {
const calendar = new Calendar();
const users = Array.from({ length: 100 }, (_, i) => `user${i}`);
await Promise.all(users.map(user => calendar.addUser(user)));
expect(calendar.getUsers()).toHaveLength(100);
});

it('Test sharing a calendar with an empty user list', async () => {
const calendar = new Calendar();
await expect(calendar.shareCalendar([])).rejects.toThrowError('No users to share calendar with');
});
});