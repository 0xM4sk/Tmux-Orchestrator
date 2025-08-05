|
## OAuth Authentication Endpoints

The OAuth authentication endpoints allow users to log in using their Google and Apple accounts. Below are detailed descriptions of each endpoint.

### Google Login

- **Endpoint**: `/google/login`
- **Method**: `GET`
- **Parameters**:
- `code`: A string representing the authorization code.
- **Error Handling**:
- If the `code` parameter is missing, a `KeyError` will be raised with the message "Missing code parameter".
- If the `code` parameter is invalid, an appropriate error message will be returned.

### Apple Callback

- **Endpoint**: `/apple/callback`
- **Method**: `GET`
- **Parameters**:
- `state`: A string representing the state token.
- **Error Handling**:
- If the `state` parameter is missing, a `KeyError` will be raised with the message "Missing state parameter".
- If the `state` parameter is invalid, an appropriate error message will be returned.

## Error Handling

Both the Google and Apple authentication endpoints include robust error handling to ensure that users are informed of any issues during the authentication process.