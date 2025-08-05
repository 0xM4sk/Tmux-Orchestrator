|
const nodemailer = require('nodemailer');

class MailService {
constructor() {
this.transporter = nodemailer.createTransport({
service: 'gmail',
auth: {
user: 'test@example.com',
pass: 'password'
}
});
}

async sendEmail(to, subject, text) {
const mailOptions = {
from: 'test@example.com',
to,
subject,
text
};

return this.transporter.sendMail(mailOptions);
}
}

module.exports = new MailService();