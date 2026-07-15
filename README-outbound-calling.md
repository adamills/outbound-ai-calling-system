# Outbound AI Calling System

A production-ready telephony integration that routes real outbound calls through an Asterisk PBX into an ElevenLabs conversational AI agent — from carrier trunk to live voice response.

## What it does

- Places outbound calls via a SIP trunk (Telnyx)
- Routes answered calls into a conversational AI voice agent (ElevenLabs)
- Logs every call outcome (answered, missed, busy, failed) to PostgreSQL
- Maps Asterisk's raw dial status into normalized, dashboard-ready call states

## Architecture

```
Caller/Campaign → SIP Trunk (Telnyx) → Asterisk PBX (PJSIP) → AI Agent (ElevenLabs)
                                              │
                                              ▼
                                     Flask API → PostgreSQL
```

## Stack

- **Telephony**: Asterisk, PJSIP, Telnyx SIP trunking
- **Voice AI**: ElevenLabs conversational agent
- **Backend**: Python, Flask
- **Database**: PostgreSQL (connection-pooled, materialized view for campaign stats)

## Call flow

1. Dialplan places the outbound call and waits for `DIALSTATUS`
2. On hangup, a non-blocking `curl` call posts the result to a Flask endpoint
3. Flask normalizes the raw Asterisk status (`ANSWER`, `NOANSWER`, `BUSY`, etc.) into a clean schema (`completed`, `missed`, `failed`)
4. The result is written to `call_logs`, and campaign-level success rates are computed via a materialized view

## Setup

```bash
pip install -r requirements.txt
psql -d your_db -f schema.sql
export DATABASE_URL="..."
python app.py
```

See `extensions-outbound.conf` for the Asterisk dialplan that connects to this system.

## Status

Actively developed. Built and tested end-to-end, including live call logging into PostgreSQL.
