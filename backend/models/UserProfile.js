|
const mongoose = require('mongoose');

const userProfileSchema = new mongoose.Schema({
userId: {
type: String,
required: true,
unique: true,
},
name: {
type: String,
required: true,
},
email: {
type: String,
required: true,
unique: true,
},
phone: {
type: String,
required: true,
},
availability: [
{
startDate: Date,
endDate: Date,
},
],
});

const UserProfile = mongoose.model('UserProfile', userProfileSchema);

module.exports = UserProfile;