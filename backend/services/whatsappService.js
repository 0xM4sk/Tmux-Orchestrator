|
const twilio = require('twilio');

const accountSid = 'your_account_sid';
const authToken = 'your_auth_token';

const client = new twilio(accountSid, authToken);

exports.sendMessage = async (to, body) => {
try {
await client.messages.create({
to: `whatsapp:+${to}`,
from: 'whatsapp:+1234567890', // Your Twilio WhatsApp number
body: body,
});
console.log('Message sent successfully');
} catch (error) {
console.error('Error sending message:', error);
}
};