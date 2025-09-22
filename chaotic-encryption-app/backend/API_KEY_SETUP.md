# 🔐 API Key Authentication Setup Guide

This guide explains how to set up and use the API key authentication system for the Chaotic Encryption App.

## 🚀 Quick Start (Development)

For development, the app automatically creates default API keys:

- **Key 1**: `dev_key_1` (permissions: encrypt, decrypt, download)
- **Key 2**: `dev_key_2` (permissions: encrypt, decrypt)

These keys are automatically available when you start the server in development mode.

## 🔧 Production Setup

### 1. Generate Production API Keys

Run the API key generator script:

```bash
cd backend
python generate_api_key.py
```

Follow the prompts to create keys with appropriate permissions.

### 2. Set Environment Variables

Create a `.env` file in the backend directory:

```bash
# .env
FLASK_ENV=production
API_KEYS='{"your_hashed_key_1":{"name":"Production Key 1","permissions":["encrypt","decrypt","download","admin"],"rate_limit":1000,"created_at":"2024-01-01T00:00:00","last_used":null}}'
```

### 3. Frontend Configuration

Set the API key in your frontend environment:

```bash
# .env (in frontend directory)
REACT_APP_API_KEY=your_generated_api_key_here
REACT_APP_API_URL=https://your-api-domain.com/api
```

## 📋 API Key Permissions

| Permission | Description |
|------------|-------------|
| `encrypt` | Can encrypt images |
| `decrypt` | Can decrypt images |
| `download` | Can download processed files |
| `admin` | Can manage API keys (create, list) |

## 🛡️ Security Features

### Rate Limiting
- Each API key has a configurable rate limit (requests per hour)
- Default: 100 requests/hour for development keys
- Production keys can have higher limits

### Request Headers
All API requests must include:
```
X-API-Key: your_api_key_here
```

### Error Responses
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: Insufficient permissions
- `429 Too Many Requests`: Rate limit exceeded

## 🔄 API Endpoints

### Protected Endpoints (Require API Key)

| Endpoint | Method | Required Permission |
|----------|--------|-------------------|
| `/api/encrypt` | POST | `encrypt` |
| `/api/decrypt` | POST | `decrypt` |
| `/api/download/<filename>` | GET | `download` |
| `/api/keys` | GET | `admin` |
| `/api/keys` | POST | `admin` |

### Public Endpoints (No Authentication)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/` | GET | API documentation |

## 🧪 Testing the API

### Using curl

```bash
# Test encryption with API key
curl -X POST http://localhost:5001/api/encrypt \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_1" \
  -d '{
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "key": "test_key",
    "algorithm": "2dlasm"
  }'

# Test without API key (should fail)
curl -X POST http://localhost:5001/api/encrypt \
  -H "Content-Type: application/json" \
  -d '{"image": "test"}'
```

### Using Postman

1. Set the `X-API-Key` header in all requests
2. Use the default development key: `dev_key_1`
3. Test different permissions with different keys

## 🔍 Monitoring and Logging

The system logs:
- API key usage
- Rate limit violations
- Permission denials
- Request timestamps

Check the console output for security events.

## 🚨 Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables for production keys**
3. **Rotate API keys regularly**
4. **Use HTTPS in production**
5. **Monitor API key usage**
6. **Set appropriate rate limits**
7. **Use least-privilege permissions**

## 🛠️ Troubleshooting

### Common Issues

**401 Unauthorized**
- Check if `X-API-Key` header is included
- Verify the API key is correct
- Ensure the key hasn't expired

**403 Forbidden**
- Check if the API key has the required permission
- Verify the endpoint requires the correct permission

**429 Too Many Requests**
- Wait for the rate limit to reset (hourly)
- Consider increasing the rate limit for the key
- Check if multiple clients are using the same key

### Debug Mode

To see detailed error messages, temporarily set:
```bash
FLASK_ENV=development
```

## 📞 Support

For issues with API key authentication:
1. Check the console logs for error messages
2. Verify environment variables are set correctly
3. Test with the default development keys first
4. Ensure the frontend is sending the correct headers

## 🔄 Migration from No Authentication

If you're upgrading from the previous version without authentication:

1. **Backend**: The new code is backward compatible - existing endpoints will work
2. **Frontend**: Update to include the `X-API-Key` header
3. **Testing**: Use the default development keys for testing
4. **Production**: Generate new production keys before deployment
