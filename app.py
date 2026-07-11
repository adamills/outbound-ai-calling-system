"""
Outbound AI Calling System - Flask Application
Integrates Asterisk, Telnyx SIP, and ElevenLabs voice AI
"""

from flask import Flask, request, jsonify
from elevenlabs import ElevenLabs
from telnyx import Telnyx
import logging
import json
from datetime import datetime
from pydantic import BaseModel, ValidationError

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize API clients
elevenlabs_client = ElevenLabs()
telnyx_client = Telnyx()

# Data models
class CallRequest(BaseModel):
    """Incoming call request model"""
    phone_number: str
    campaign_id: str
    script_id: str
    voice_id: str = "default"

class CallLog(BaseModel):
    """Call log model for analytics"""
    call_id: str
    phone_number: str
    campaign_id: str
    duration: int
    status: str
    timestamp: str

# In-memory call logs (use database in production)
call_logs = []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/calls/outbound', methods=['POST'])
def initiate_outbound_call():
    """Initiate an outbound call via Telnyx SIP trunk"""
    try:
        data = request.get_json()
        call_request = CallRequest(**data)
        
        logger.info(f"Initiating outbound call to {call_request.phone_number}")
        
        # Create call via Telnyx
        call_response = telnyx_client.call_control.create(
            to=call_request.phone_number,
            from_='your_telnyx_number',
            connection_id='your_connection_id'
        )
        
        call_id = call_response.data.call_token
        
        return jsonify({
            'call_id': call_id,
            'status': 'initiated',
            'phone_number': call_request.phone_number,
            'timestamp': datetime.now().isoformat()
        }), 202
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': 'Invalid request data', 'details': str(e)}), 400
    except Exception as e:
        logger.error(f"Error initiating call: {e}")
        return jsonify({'error': 'Failed to initiate call'}), 500

@app.route('/api/calls/<call_id>/speak', methods=['POST'])
def speak_during_call(call_id):
    """Play AI-generated speech during active call"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        voice_id = data.get('voice_id', 'default')
        
        logger.info(f"Generating speech for call {call_id}: {text[:50]}...")
        
        # Generate speech using ElevenLabs
        audio = elevenlabs_client.generate(
            text=text,
            voice=voice_id
        )
        
        # Stream audio to call
        # (Implementation depends on Asterisk AGI/AMI setup)
        
        return jsonify({
            'call_id': call_id,
            'status': 'speaking',
            'text_length': len(text)
        }), 200
        
    except Exception as e:
        logger.error(f"Error during speak: {e}")
        return jsonify({'error': 'Failed to generate speech'}), 500

@app.route('/api/calls/<call_id>/hangup', methods=['POST'])
def hangup_call(call_id):
    """End an active call"""
    try:
        logger.info(f"Hanging up call {call_id}")
        
        # Hangup via Telnyx
        telnyx_client.call_control.hangup(call_id)
        
        return jsonify({
            'call_id': call_id,
            'status': 'terminated',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error hanging up call: {e}")
        return jsonify({'error': 'Failed to hangup call'}), 500

@app.route('/api/calls/logs', methods=['GET'])
def get_call_logs():
    """Retrieve call logs for analytics dashboard"""
    try:
        campaign_id = request.args.get('campaign_id')
        limit = int(request.args.get('limit', 100))
        
        logs = call_logs
        if campaign_id:
            logs = [log for log in logs if log['campaign_id'] == campaign_id]
        
        return jsonify({
            'total': len(logs),
            'logs': logs[-limit:],
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        return jsonify({'error': 'Failed to retrieve logs'}), 500

@app.route('/api/calls/logs', methods=['POST'])
def log_call_event():
    """Log a call event for analytics"""
    try:
        data = request.get_json()
        call_log = CallLog(**data)
        
        call_logs.append(call_log.dict())
        logger.info(f"Logged call {call_log.call_id}")
        
        return jsonify({
            'status': 'logged',
            'call_id': call_log.call_id
        }), 201
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': 'Invalid log data'}), 400
    except Exception as e:
        logger.error(f"Error logging call: {e}")
        return jsonify({'error': 'Failed to log call'}), 500

@app.route('/api/campaigns', methods=['GET'])
def list_campaigns():
    """List active campaigns"""
    # Placeholder - implement with database
    return jsonify({
        'campaigns': [],
        'total': 0
    }), 200

@app.route('/api/campaigns/<campaign_id>/stats', methods=['GET'])
def get_campaign_stats(campaign_id):
    """Get statistics for a specific campaign"""
    try:
        campaign_logs = [log for log in call_logs if log.get('campaign_id') == campaign_id]
        
        total_calls = len(campaign_logs)
        completed_calls = len([log for log in campaign_logs if log.get('status') == 'completed'])
        total_duration = sum(log.get('duration', 0) for log in campaign_logs)
        
        return jsonify({
            'campaign_id': campaign_id,
            'total_calls': total_calls,
            'completed_calls': completed_calls,
            'completion_rate': (completed_calls / total_calls * 100) if total_calls > 0 else 0,
            'total_duration_seconds': total_duration,
            'average_duration': total_duration / total_calls if total_calls > 0 else 0
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting campaign stats: {e}")
        return jsonify({'error': 'Failed to retrieve stats'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development mode
    app.run(host='0.0.0.0', port=5000, debug=True)
