|
# API Documentation

## Endpoints

- **GET /events**
- Returns a list of all events.
- Requires authentication.

- **POST /events**
- Creates a new event.
- Requires authentication.

- **GET /events/<int:event_id>**
- Retrieves details for a specific event.
- Requires authentication.

- **PUT /events/<int:event_id>**
- Updates an existing event.
- Requires authentication.

- **DELETE /events/<int:event_id>**
- Deletes an event.
- Requires authentication.

- **POST /register**
- Registers a user for an event.
- Requires authentication.

- **DELETE /unregister**
- Unregisters a user from an event.
- Requires authentication.