|
# Event Cancellation

## Canceling an Event

### Request
- **Endpoint**: `/api/events/{event_id}/cancel`
- **Method**: `DELETE`
- **Headers**:
- `Authorization`: Bearer <access_token>

### Response
- **Success**: 204 No Content

- **Failure**: 404 Not Found
```json
{
"message": "Event not found"
}
```