|
# OAuth Authentication Endpoints

## Overview

This document outlines the new OAuth authentication endpoints added to the Strangers Calendar App. These endpoints support Google and Apple authentication methods.

## Endpoints

### Google Authentication

- **Endpoint**: `/api/auth/google`
- **Method**: `POST`
- **Description**: Initiates the Google OAuth flow.
- **Request Body**:
```json
{
"redirect_uri": "string"
}
```
- **Response**:
```json
{
"url": "string"
}
```

### Apple Authentication

- **Endpoint**: `/api/auth/apple`
- **Method**: `POST`
- **Description**: Initiates the Apple OAuth flow.
- **Request Body**:
```json
{
"redirect_uri": "string"
}
```
- **Response**:
```json
{
"url": "string"
}
```

## Usage

To use these endpoints, make a POST request to the specified URL with the required redirect URI. The response will contain a URL that should be opened in a web browser to complete the OAuth flow.

### Example