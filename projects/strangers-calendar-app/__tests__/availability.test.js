|
const availabilityService = require('../src/services/availability');

describe('Availability Input', () => {
it('should handle overlapping windows', async () => {
// Mock the necessary data and functions
const windows = [
{ start: '09:00', end: '12:00' },
{ start: '11:00', end: '14:00' }
];

// Call the function to be tested
await availabilityService.checkAvailability(windows);

// Verify the expected behavior
expect(availabilityService).toHaveBeenCalledWith('overlapping-windows');
});

it('should handle non-standard time formats', async () => {
// Mock the necessary data and functions
const windows = [
{ start: '9AM', end: '12PM' },
{ start: '11 AM', end: '2 PM' }
];

// Call the function to be tested
await availabilityService.checkAvailability(windows);

// Verify the expected behavior
expect(availabilityService).toHaveBeenCalledWith('non-standard-time-formats');
});
});