from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Firebase Admin
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone = os.getenv('TWILIO_PHONE')

app = Flask(__name__)
client = Client(account_sid, auth_token)

# Messages Collection Endpoints
@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        name = request.args.get('name')
        order = request.args.get('order', 'desc')  # 'desc' or 'asc'
        
        # Start with base query
        query = db.collection('messages')
        
        # Apply filters if provided
        if name:
            query = query.where('name', '==', name)
            
        # Order by createdAt and limit
        direction = firestore.Query.DESCENDING if order.lower() == 'desc' else firestore.Query.ASCENDING
        query = query.order_by('createdAt', direction=direction).limit(limit)
        
        # Execute query
        docs = query.stream()
        
        # Convert to list of dictionaries
        messages = []
        for doc in docs:
            message = doc.to_dict()
            message['id'] = doc.id
            # Convert Timestamp to ISO format string
            if 'createdAt' in message:
                message['createdAt'] = message['createdAt'].isoformat()
            messages.append(message)
            
        return jsonify({
            'status': 'success',
            'messages': messages,
            'order': order
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/messages', methods=['POST'])
def create_message():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data or 'message' not in data:
            return jsonify({'error': 'Missing required fields: name and message'}), 400
            
        # Create message document
        message_data = {
            'name': data['name'],
            'message': data['message'],
            'createdAt': datetime.utcnow()
        }
        
        # Add to Firestore
        doc_ref = db.collection('messages').document()
        doc_ref.set(message_data)
        
        # Get the created document
        doc = doc_ref.get()
        message = doc.to_dict()
        message['id'] = doc.id
        message['createdAt'] = message['createdAt'].isoformat()
        
        return jsonify({
            'status': 'success',
            'message': message
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/messages/count', methods=['GET'])
def get_message_count():
    try:
        # Get query parameters
        name = request.args.get('name')
        
        # Start with base query
        query = db.collection('messages')
        
        # Apply filter if provided
        if name:
            query = query.where('name', '==', name)
            
        # Get count using a different approach
        docs = query.stream()
        count = sum(1 for _ in docs)
        
        return jsonify({
            'status': 'success',
            'count': count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to send an SMS
@app.route('/send_sms', methods=['POST'])
def send_sms():
    try:
        data = request.get_json(force=True)  # force=True to accept any content type
        if not data or 'to' not in data:
            return jsonify({'error': 'Missing required field: to'}), 400
            
        to_number = data['to']
        message_body = data.get('message', '')  # Make message optional
        
        message = client.messages.create(
            from_=twilio_phone,
            to=to_number,
            body=message_body
        )
        
        return jsonify({
            'status': 'success',
            'message_sid': message.sid,
            'to': to_number,
            'from': twilio_phone
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to handle incoming SMS
@app.route('/sms', methods=['POST'])
def sms_reply():
    incoming_message = request.form['Body']
    response = MessagingResponse()

    # Example action upon receiving an SMS
    if 'hello' in incoming_message.lower():
        response.message("Hi there! How can I help you?")
    else:
        response.message("Thank you for your message!")

    return str(response)

if __name__ == '__main__':
    app.run(debug=True)