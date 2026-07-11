from flask import Flask, request, jsonify
from app_db import SessionLocal, CallLog
import datetime

app = Flask(__name__)

@app.route('/health')
def health():
    return {'status':'ok','time':datetime.datetime.now().isoformat()}

@app.route('/api/calls/logs', methods=['POST'])
def log_call():
    data = request.get_json()
    db = SessionLocal()
    log = CallLog(**data)
    db.add(log)
    db.commit()
  
@app.route('/api/calls/logs', methods=['GET'])
def get_logs():
    db = SessionLocal()
    logs = db.query(CallLog).all()
    return jsonify([{
        'call_id': l.call_id,
        'phone_number': l.phone_number,
        'campaign_id': l.campaign_id,
        'duration': l.duration,
        'status': l.status,
        'timestamp': l.timestamp.isoformat() if l.timestamp else None
    } for l in logs])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
