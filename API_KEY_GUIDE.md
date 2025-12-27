# API Key Protection Guide

## Overview

This API supports optional API key authentication to protect endpoints. When enabled, most API endpoints require a valid API key in the request header.

## Configuration

### Enable API Key Protection

Edit your `.env` file:

```env
# Enable API key authentication
ENABLE_API_KEY=true

# Set your secret API key
X_API_KEY=your_secret_key_here
```

**Important:** Choose a strong, random API key. Example:
```bash
# Generate a secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Restart the Service

After changing the configuration, restart the service:

```bash
docker-compose restart
```

## Protected vs Unprotected Endpoints

### Unprotected Endpoints (No API Key Required)

These endpoints are always accessible without an API key:

- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI schema
- `GET /auth/login` - Get OAuth authorization URL
- `GET /auth/callback` - OAuth callback (all variants)
- `POST /auth/callback` - OAuth callback (POST variant)

**Reason:** These endpoints are needed for:
- Service health monitoring
- API documentation access
- Initial OAuth authentication flow

### Protected Endpoints (API Key Required)

When `ENABLE_API_KEY=true`, these endpoints require a valid API key:

#### Authentication Endpoints
- `GET /auth/status` - Check authentication status
- `POST /auth/logout` - Logout and clear token cache

#### Task List Endpoints
- `GET /lists` - Get all task lists
- `POST /lists` - Create a new task list
- `GET /lists/{list_id}` - Get a specific task list
- `PATCH /lists/{list_id}` - Update a task list
- `DELETE /lists/{list_id}` - Delete a task list
- `GET /lists/{list_id}/tasks` - Get tasks in a list
- `POST /lists/{list_id}/tasks` - Create a task in a list

#### Task Endpoints
- `GET /tasks/{task_id}` - Get a specific task
- `PATCH /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task

## Using the API Key

### HTTP Header

Include the API key in the `X-API-KEY` header:

```bash
curl -H "X-API-KEY: your_secret_key_here" http://localhost:8000/auth/status
```

### Example Requests

#### Check Authentication Status (Protected)

```bash
# Without API key - Returns 401 Unauthorized
curl http://localhost:8000/auth/status

# With invalid API key - Returns 403 Forbidden
curl -H "X-API-KEY: wrong_key" http://localhost:8000/auth/status

# With valid API key - Returns 200 OK
curl -H "X-API-KEY: your_secret_key_here" http://localhost:8000/auth/status
```

#### Get Task Lists (Protected)

```bash
curl -H "X-API-KEY: your_secret_key_here" http://localhost:8000/lists
```

#### Access Documentation (Unprotected)

```bash
# No API key needed for documentation
curl http://localhost:8000/docs
```

## Error Responses

### 401 Unauthorized - Missing API Key

```json
{
  "detail": "Missing X-API-KEY header"
}
```

**Solution:** Include the `X-API-KEY` header in your request.

### 403 Forbidden - Invalid API Key

```json
{
  "detail": "Invalid API key"
}
```

**Solution:** Verify that your API key matches the value in `.env` file.

## Security Best Practices

1. **Use Strong Keys**: Generate random, cryptographically secure API keys
2. **Keep Keys Secret**: Never commit API keys to version control
3. **Rotate Keys Regularly**: Change API keys periodically
4. **Use HTTPS**: Always use HTTPS in production to protect API keys in transit
5. **Limit Key Exposure**: Only share API keys with authorized users/applications
6. **Monitor Access**: Log and monitor API access for suspicious activity

## Verification

Use the included verification script to test API key protection:

```bash
# Edit the script to set your API key
nano verify_api_key_protection.py

# Run the verification
python verify_api_key_protection.py
```

The script will test all endpoints and verify that:
- Unprotected endpoints are accessible without API key
- Protected endpoints reject requests without API key (401)
- Protected endpoints reject requests with invalid API key (403)
- Protected endpoints accept requests with valid API key (200)

## Disabling API Key Protection

To disable API key protection, set in `.env`:

```env
ENABLE_API_KEY=false
```

Then restart the service:

```bash
docker-compose restart
```

When disabled, all endpoints (except those requiring Microsoft To Do authentication) are accessible without an API key.

## Integration with Microsoft To Do Authentication

API key protection is **independent** of Microsoft To Do OAuth authentication:

1. **API Key** - Controls access to the API gateway itself
2. **OAuth Token** - Controls access to Microsoft To Do data

Both layers work together:
- First, the API key is checked (if enabled)
- Then, the Microsoft To Do OAuth token is verified

This allows you to:
- Control who can access your API gateway (API key)
- While still requiring proper Microsoft account authorization (OAuth)
