|
# Event Search

## Searching for Events

### Request
- **Endpoint**: `/api/events/search`
- **Method**: `GET`
- **Query Parameters**:
- `query`: search query string

### Response
- **Success**: 200 OK
```json
{
"events": [
{
"id": "123",
"title": "Event Title",
"description": "Event Description",
"start_time": "2023-10-01T12:00:00Z",
"end_time": "2023-10-01T14:00:00Z"
}
]
}
```

- **Failure**: 400 Bad Request
```json
{
"message": "Invalid search query"
}
```