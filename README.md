# Flask API with Firestore and Twilio Integration

This Flask application provides a RESTful API for managing messages in Firestore and handling SMS communications via Twilio.

## Features

- Firestore message management (CRUD operations)
- Twilio SMS integration
- Environment variable configuration
- Error handling and validation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```env
# Twilio Credentials
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE=your_twilio_phone_number

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

3. Set up Firebase:
   - Download your service account key from Firebase Console
   - Place the JSON file in your project directory
   - Update `FIREBASE_CREDENTIALS_PATH` in `.env` to point to your credentials file

4. Run the application:
```bash
python server.py
```

## API Endpoints

### Messages Collection

#### Get Messages
```http
GET /messages
```

Query Parameters:
- `limit` (optional): Number of messages to return (default: 50)
- `name` (optional): Filter messages by name
- `order` (optional): Sort order - 'desc' (newest first) or 'asc' (oldest first)

Example:
```bash
# Get latest 50 messages
GET /messages

# Get 10 oldest messages
GET /messages?limit=10&order=asc

# Get messages by name
GET /messages?name=Joe%20Sanjo
```

Response:
```json
{
    "status": "success",
    "messages": [
        {
            "id": "message_id",
            "name": "Joe Sanjo",
            "message": "This is an awesome discussion!",
            "createdAt": "2024-03-14T12:00:00Z"
        }
    ],
    "order": "desc"
}
```

#### Create Message
```http
POST /messages
```

Request Body:
```json
{
    "name": "Joe Sanjo",
    "message": "This is an awesome discussion!"
}
```

Response:
```json
{
    "status": "success",
    "message": {
        "id": "message_id",
        "name": "Joe Sanjo",
        "message": "This is an awesome discussion!",
        "createdAt": "2024-03-14T12:00:00Z"
    }
}
```

#### Get Message Count
```http
GET /messages/count
```

Query Parameters:
- `name` (optional): Count messages by specific name

Example:
```bash
# Get total count
GET /messages/count

# Get count by name
GET /messages/count?name=Joe%20Sanjo
```

Response:
```json
{
    "status": "success",
    "count": 42
}
```

### Twilio Integration

#### Send SMS
```http
POST /send_sms
```

Request Body:
```json
{
    "to": "+1234567890",
    "message": "Hello from the API!"
}
```

Response:
```json
{
    "status": "success",
    "message_sid": "SM123...",
    "to": "+1234567890",
    "from": "+1987654321"
}
```

#### Handle Incoming SMS
```http
POST /sms
```

The endpoint automatically responds to incoming SMS messages:
- If message contains "hello": Responds with "Hi there! How can I help you?"
- Otherwise: Responds with "Thank you for your message!"

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 201: Created (for POST requests)
- 400: Bad Request (missing or invalid parameters)
- 500: Internal Server Error

Error Response Format:
```json
{
    "error": "Error message description"
}
```

## Security Notes

1. Never commit the `.env` file or Firebase credentials to version control
2. Add the following to your `.gitignore`:
```
.env
firebase-credentials.json
```

## Dependencies

- Flask
- Firebase Admin SDK
- Twilio
- python-dotenv 
