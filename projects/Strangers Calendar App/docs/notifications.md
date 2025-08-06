|
# Notifications

## Sending a Notification

### Request
- **Endpoint**: `/api/notifications`
- **Method**: `POST`
- **Headers**:
- `Authorization`: Bearer <access_token>
- **Body**:
```json
{
"title": "Notification Title",
"message": "Notification Message"
}
```

### Response
- **Success**: 201 Created
```json
{
"message": "Notification sent successfully"
}
```

- **Failure**: 400 Bad Request
```json
{
"message": "Invalid notification data"
}
```