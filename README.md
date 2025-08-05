|
# Strangers Calendar App

## Overview

The Strangers Calendar App is a platform that allows users to create, manage, and share events with others. This documentation provides details on how to interact with the backend API.

## Installation

To run the application locally, follow these steps:

1. Clone the repository:
```sh
git clone https://github.com/yourusername/strangers-calendar-app.git
cd strangers-calendar-app
```

2. Set up a virtual environment (optional but recommended):
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies:
```sh
pip install -r requirements.txt
```

4. Run the application:
```sh
python backend/app.py
```

## API Documentation

### OAuth Authentication Endpoints

- **Endpoint**: `/auth/login`
- **Method**: `POST`
- **Description**: Logs in a user using their credentials.
- **Request Body**:
```json
{
"email": "user@example.com",
"password": "password123"
}
```
- **Response**:
```json
{
"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
"token_type": "Bearer"
}
```

- **Endpoint**: `/auth/register`
- **Method**: `POST`
- **Description**: Registers a new user.
- **Request Body**:
```json
{
"email": "user@example.com",
"password": "password123",
"name": "John Doe"
}
```
- **Response**:
```json
{
"message": "User registered successfully"
}
```

- **Endpoint**: `/auth/logout`
- **Method**: `POST`
- **Description**: Logs out a user.
- **Headers**:
```json
{
"Authorization": "Bearer <access_token>"
}
```
- **Response**:
```json
{
"message": "User logged out successfully"
}
```

## Contributing

Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.