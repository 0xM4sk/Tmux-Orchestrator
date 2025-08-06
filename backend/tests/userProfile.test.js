|
const mongoose = require('mongoose');
const { createUserProfile, updateUserProfile } = require('../services/userProfileService');

beforeAll(async () => {
await mongoose.connect('mongodb://localhost/test', { useNewUrlParser: true, useUnifiedTopology: true });
});

afterAll(async () => {
await mongoose.connection.close();
});

test('Create user profile', async () => {
const userProfile = await createUserProfile('user123', 'John Doe', 'john@example.com', '+1234567890');
expect(userProfile).toHaveProperty('userId', 'user123');
expect(userProfile).toHaveProperty('name', 'John Doe');
expect(userProfile).toHaveProperty('email', 'john@example.com');
expect(userProfile).toHaveProperty('phone', '+1234567890');
});

test('Update user profile', async () => {
const userProfile = await createUserProfile('user456', 'Jane Doe', 'jane@example.com', '+0987654321');
const updatedUserProfile = await updateUserProfile(userProfile.userId, { name: 'Jane Smith' });
expect(updatedUserProfile).toHaveProperty('name', 'Jane Smith');
});