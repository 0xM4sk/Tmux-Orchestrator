|
const { Calendar } = require('../../src/models/Calendar');
const { User } = require('../../src/models/User');

describe('Edge Cases in Calendar Creation and Sharing', () => {
it('Test calendar creation with large number of users', async () => {
const users = Array.from({ length: 100 }, (_, i) => new User(`user${i}`));
expect(async () => {
await Calendar.create(users);
}).not.toThrow();
});

it('Test sharing a calendar with an empty user list', async () => {
const calendar = new Calendar();
expect(async () => {
await calendar.share([]);
}).not.toThrow();
});
});