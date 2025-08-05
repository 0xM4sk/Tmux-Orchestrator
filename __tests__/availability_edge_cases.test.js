|
// Additional test cases for availability edge scenarios
const { Availability } = require('../src/availability');
const { expect } = require('@jest/globals');

describe('Availability Edge Cases', () => {
it('Test availability input with overlapping windows', async () => {
const availability = new Availability();
await availability.addWindow({ start: '09:00', end: '12:00' });
await expect(availability.addWindow({ start: '11:00', end: '13:00' })).rejects.toThrowError('Overlapping windows');
});

it('Test availability input with non-standard time formats', async () => {
const availability = new Availability();
await expect(availability.addWindow({ start: '9 AM', end: '5 PM' })).resolves.toBeUndefined();
});
});