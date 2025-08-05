|
const whatsappService = require('../services/whatsappService');

exports.sendWhatsAppMessage = async (req, res) => {
try {
const { phoneNumber, message } = req.body;
await whatsappService.sendMessage(phoneNumber, message);
res.status(200).json({ success: true, message: 'Message sent' });
} catch (error) {
res.status(500).json({ success: false, error: error.message });
}
};