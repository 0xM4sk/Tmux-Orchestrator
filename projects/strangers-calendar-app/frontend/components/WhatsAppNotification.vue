|
<template>
<div>
<input v-model="phoneNumber" type="text" placeholder="Phone Number">
<button @click="sendNotification">Send Notification</button>
</div>
</template>

<script>
import { send_whatsapp_message } from '@/services/whatsapp'

export default {
data() {
return {
phoneNumber: ''
}
},
methods: {
async sendNotification() {
await send_whatsapp_message(this.phoneNumber, 'Hello, this is a test message')
alert('Message sent successfully')
}
}
}
</script>