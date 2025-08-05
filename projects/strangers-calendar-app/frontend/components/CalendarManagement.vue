|
<template>
<div>
<button @click="createEvent">Create Event</button>
<button @click="shareCalendar">Share Calendar</button>
</div>
</template>

<script>
import { temp_calendar, share_calendar } from '@/services/calendar_service'

export default {
methods: {
createEvent() {
// Logic to add event to calendar
},
async shareCalendar() {
await share_calendar(temp_calendar.id, 'user@example.com')
alert('Calendar shared successfully')
}
}
}
</script>