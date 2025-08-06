|
# OAuth Authentication Endpoints

## Google Authentication

### Request
- **Endpoint**: `/api/auth/google`
- **Method**: `GET`

### Response
- **Success**: 200 OK
```json
{
"message": "Successfully authenticated with Google",
"user": {
"id": "12345",
"email": "example@gmail.com",
"name": "John Doe"
}
}
```

- **Failure**: 401 Unauthorized
```json
{
"message": "Failed to authenticate with Google"
}
```

## Apple Authentication

### Request
- **Endpoint**: `/api/auth/apple`
- **Method**: `GET`

### Response
- **Success**: 200 OK
```json
{
"message": "Successfully authenticated with Apple",
"user": {
"id": "67890",
"email": "example@apple.com",
"name": "Jane Doe"
}
}
```

- **Failure**: 401 Unauthorized
```json
{
"message": "Failed to authenticate with Apple"
}
```