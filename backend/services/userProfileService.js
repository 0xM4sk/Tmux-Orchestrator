|
const UserProfile = require('../models/UserProfile');

async function createUserProfile(userId, name, email, phone) {
return await UserProfile.create({ userId, name, email, phone });
}

async function updateUserProfile(userId, updates) {
return await UserProfile.findOneAndUpdate({ userId }, updates, { new: true });
}

module.exports = {
createUserProfile,
updateUserProfile,
};