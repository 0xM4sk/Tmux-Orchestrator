|
# Event Management

## Creating an Event

### Request
- **Endpoint**: `/api/events`
- **Method**: `POST`
- **Headers**:
- `Authorization`: Bearer <access_token>
- **Body**:
```json
{
"title": "Event Title",
"description": "Event Description",
"start_time": "2023-10-01T12:00:00Z",
"end_time": "2023-10-01T14:00:00Z"
}
```

### Response
- **Success**: 201 Created
```json
{
"message": "Event created successfully",
"event": {
"id": "123",
"title": "Event Title",
"description": "Event Description",
"start_time": "2023-10-01T12:00:00Z",
"end_time": "2023-10-01T14:00:00Z"
}
}
```

- **Failure**: 400 Bad Request
```json
{
"message": "Invalid event data"
}
```

## Inviting Others to Events

### Request
- **Endpoint**: `/api/events/{event_id}/invite`
- **Method**: `POST`
- **Headers**:
- `Authorization`: Bearer <access_token>
- **Body**:
```json
{
"email": "example@gmail.com"
}
```

### Response
- **Success**: 200 OK
```json
{
"message": "Invitation sent successfully"
}
```

- **Failure**: 404 Not Found
```json
{
"message": "Event not found"
}
```