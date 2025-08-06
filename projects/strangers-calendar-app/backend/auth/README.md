|
# OAuth Authentication

## Endpoints

- **Login**: `/api/auth/login`
- **Method**: `POST`
- **Request Body**:
```json
{
"provider": "google|apple",
"token": "string"
}
```
- **Response**:
- **Success (200)**:
```json
{
"message": "Login successful",
"user_id": "string",
"access_token": "string"
}
```
- **Error (401)**:
```json
{
"error": "Invalid token"
}
```

- **Logout**: `/api/auth/logout`
- **Method**: `POST`
- **Request Body**:
```json
{
"user_id": "string",
"access_token": "string"
}
```
- **Response**:
- **Success (200)**:
```json
{
"message": "Logout successful"
}
```
- **Error (401)**:
```json
{
"error": "Invalid token"
}
```

## Notes
- Ensure that the `provider` parameter is either `google` or `apple`.
- The `token` must be a valid authentication token from the respective provider.