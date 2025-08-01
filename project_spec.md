PROJECT: Strangers' Calendar App

GOAL: Build a web application that allows strangers to create temporary shared calendars, authenticate via OAuth (Google, Apple, etc.), and optionally link phone numbers and WhatsApp for notifications. The app should enable users to display their availability windows and automatically find intersections of availability among a group.

CONSTRAINTS:
- Use existing database schema where possible, but extend as needed for calendar and user integration features
- Follow current code patterns and architecture
- Commit every 30 minutes
- Write comprehensive tests for all new features
- Ensure privacy: temporary calendars should expire and be deleted after a set period
- Do not require users to register permanent accounts; allow ephemeral/guest access via OAuth

DELIVERABLES:
1. OAuth authentication endpoints (Google, Apple, etc.)
2. Phone number and WhatsApp integration for notifications and reminders
3. Temporary calendar creation and sharing functionality
4. UI and backend for users to input and display their availability windows
5. Algorithm to compute and display intersection of availability among invited users
6. Automatic expiration and cleanup of temporary calendars
7. Tests for all new features and integrations
