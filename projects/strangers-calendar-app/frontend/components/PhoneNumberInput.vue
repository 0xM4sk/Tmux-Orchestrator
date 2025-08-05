|
<template>
<div>
<input v-model="phoneNumber" type="text" placeholder="Phone Number">
<button @click="validateNumber">Validate</button>
<p v-if="isValid">Valid Phone Number</p>
<p v-else>Invalid Phone Number</p>
</div>
</template>

<script>
import { validate_phone_number } from '@/utils/phone_validation'

export default {
data() {
return {
phoneNumber: '',
isValid: false
}
},
methods: {
validateNumber() {
this.isValid = validate_phone_number(this.phoneNumber)
}
}
}
</script>