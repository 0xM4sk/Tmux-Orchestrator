|
# User Profile Management

## Updating User Profile

### Request
- **Endpoint**: `/api/users/profile`
- **Method**: `PUT`
- **Headers**:
- `Authorization`: Bearer <access_token>
- **Body**:
```json
{
"name": "New Name",
"email": "new@example.com"
}
```

### Response
- **Success**: 200 OK
```json
{
"message": "Profile updated successfully",
"user": {
"id": "123",
"name": "New Name",
"email": "new@example.com"
}
}
```

- **Failure**: 400 Bad Request
```json
{
"message": "Invalid user data"
}
```

## Retrieving User Profile

### Request
- **Endpoint**: `/api/users/profile`
- **Method**: `GET`
- **Headers**:
- `Authorization`: Bearer <access_token>

### Response
- **Success**: 200 OK
```json
{
"user": {
"id": "123",
"name": "User Name",
"email": "user@example.com"
}
}
```