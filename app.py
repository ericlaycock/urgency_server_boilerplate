from flask import Flask, request, jsonify
import threading
import time
import os
import tempfile
import traceback
import json
import openai
from faster_whisper import WhisperModel
import torch
import uuid
import logging

app = Flask(__name__)

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI and Whisper as before
openai_key = os.environ.get("OPENAI_KEY")
if openai_key is None:
    raise ValueError("OPENAI_KEY environment variable not set!")
client = openai.OpenAI(api_key=openai_key)

whisper_model = WhisperModel(
    "jacktol/whisper-medium.en-fine-tuned-for-ATC-faster-whisper",
    device="cuda" if torch.cuda.is_available() else "cpu",
    compute_type="float16" if torch.cuda.is_available() else "float32"
)

# Dictionary to hold session data
sessions = {}
session_lock = threading.Lock()

def summarize_transcript(transcript: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize the following transcript by a pilot in maximum 2 sentences."},
            {"role": "user", "content": transcript}
        ]
    )
    return response.choices[0].message.content.strip()

def assess_urgency(chunk_transcript: str, current_summary: str) -> int:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in aviation communications. Rate the urgency level on a scale of 1-10, where 10 is immediate emergency. Maintain a moderate urgency level where ongoing attention or caution is warranted"},
            {"role": "user", "content": f"Previous context: {current_summary}\nPilot's last communication: {chunk_transcript}\nProvide only the number."}
        ]
    )
    try:
        return int(response.choices[0].message.content.strip())
    except Exception as e:
        print("Error parsing urgency:", e)
        return -1

def process_audio_clip(file_data: bytes, session_id: str):
    temp_filename = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(file_data)
            temp_filename = tmp.name

        segments, _ = whisper_model.transcribe(temp_filename, language="en")
        chunk_transcript = " ".join([segment.text for segment in segments])
        urgency = assess_urgency(chunk_transcript, sessions[session_id]["current_summary"])
        
        # Just update the transcript, don't worry about summary
        with session_lock:
            sessions[session_id]["complete_transcript"] += " " + chunk_transcript
        
        return chunk_transcript, urgency
    except Exception as e:
        print("Error processing clip:", e, traceback.format_exc())
        return None, None
    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.route('/startSession', methods=['POST'])
def start_session():
    """Start a new session and return a unique session_id."""
    session_id = str(uuid.uuid4())
    logger.info(f"Starting new session with ID: {session_id}")
    with session_lock:
        sessions[session_id] = {"complete_transcript": "", "current_summary": ""}
    return jsonify({"session_id": session_id})

@app.route('/uploadAudio', methods=['POST'])
def upload_audio():
    session_id = request.args.get("session_id")
    logger.info(f"Received audio upload request for session: {session_id}")
    if not session_id or session_id not in sessions:
        logger.error(f"Invalid session ID: {session_id}")
        return jsonify({"error": "Invalid or missing session_id"}), 400
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    file_data = file.read()
    chunk_transcript, urgency = process_audio_clip(file_data, session_id)
    if chunk_transcript is None:
        return jsonify({"error": "Processing error"}), 500
    return jsonify({
        "chunk_transcript": chunk_transcript,
        "urgency": urgency,
        "current_summary": sessions[session_id]["current_summary"]
    })

@app.route('/sessionStatus', methods=['GET'])
def session_status():
    session_id = request.args.get("session_id")
    logger.info(f"Session status requested for session: {session_id}")
    if not session_id or session_id not in sessions:
        logger.error(f"Invalid session ID: {session_id}")
        return jsonify({"error": "Invalid or missing session_id"}), 400
    with session_lock:
        return jsonify(sessions[session_id])

@app.route('/getSummary', methods=['GET'])
def get_summary():
    """Get a fresh summary for the session's transcript."""
    session_id = request.args.get("session_id")
    logger.info(f"Summary requested for session: {session_id}")
    if not session_id or session_id not in sessions:
        logger.error(f"Invalid session ID: {session_id}")
        return jsonify({"error": "Invalid or missing session_id"}), 400
    
    with session_lock:
        complete_transcript = sessions[session_id]["complete_transcript"]
        summary = summarize_transcript(complete_transcript)
        sessions[session_id]["current_summary"] = summary
        logger.info(f"Summary generated for session: {session_id}")
        return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
