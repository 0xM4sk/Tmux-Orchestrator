|
# OAuth Authentication Implementation for Strangers Calendar App

## Overview
This section provides an overview of the OAuth authentication implementation in our application.

### Endpoints

1. **Login**
- **Endpoint**: `/auth/login`
- **Method**: `POST`
- **Request Body**:
```json
{
"email": "user@example.com",
"password": "password"
}
```
- **Response**:
- On success: HTTP 200 OK with a JSON object `{ "token": "your_token_here" }`
- On failure: HTTP 401 Unauthorized

2. **Logout**
- **Endpoint**: `/auth/logout`
- **Method**: `POST`
- **Response**:
- On success: HTTP 200 OK with a JSON object `{ "message": "Logged out successfully" }`

## Implementation Details
The OAuth authentication implementation is built using Flask and includes the following components:

- **OAuth Login Endpoint**: Handles user login requests.
- **OAuth Logout Endpoint**: Handles user logout requests.

Ensure that all tests are passing before merging this implementation into the main branch.