from flask import Flask, request, render_template, send_file, jsonify, redirect
import subprocess
import os
import shutil
import uuid
import imageio_ffmpeg as ffmpeg
import threading
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
DOWNLOAD_DIR = './downloads'

# Store session data in a dictionary
sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_song():
    song_url = request.form['song_url']
    session_id = str(uuid.uuid4())
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    
    try:
        # Create a unique download directory for this session
        os.makedirs(session_download_dir, exist_ok=True)
        
        # Ensure ffmpeg is available
        ffmpeg_executable = ffmpeg.get_ffmpeg_exe()
        
        # spotdl command to download the content
        result = subprocess.run([
            'spotdl', 
            '--ffmpeg', ffmpeg_executable, 
            song_url, 
            '--output', os.path.join(session_download_dir, '{artist} - {title}.{ext}')
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Check if the process was successful
        if result.returncode == 0:
            return redirect(f"/download_zip/{session_id}")
            return jsonify({'success': True, 'session_id': session_id})
        else:
            return jsonify({'success': False, 'error_message': f"Error: {result.stderr}"})
    except Exception as e:
        return jsonify({'success': False, 'error_message': f"Unexpected error: {str(e)}"})


@app.route('/get_id', methods=['GET'])
def get_id():
    session_id = request.args.get('session_id')
    if session_id in sessions:
        return jsonify({'success': True, 'session_id': session_id})
    return jsonify({'success': False, 'error_message': 'Invalid session ID'})

@app.route('/download_progress/<session_id>')
def download_progress(session_id):
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    if session_id not in sessions:
        return jsonify({'success': False, 'error_message': 'Invalid session ID'})
    try:
        total_items = len(os.listdir(session_download_dir))
        downloaded_items = len([name for name in os.listdir(session_download_dir) if os.path.isfile(os.path.join(session_download_dir, name))])
        percentage = int((downloaded_items / total_items) * 100) if total_items > 0 else 0
        sessions[session_id]['progress'] = percentage

        return jsonify({'success': True, 'percentage': percentage, 'total_items': total_items})
    except Exception as e:
        return jsonify({'success': False, 'error_message': str(e)})

@app.route('/download_zip/<session_id>')
def download_zip(session_id):
    if session_id not in sessions:
        return jsonify({'success': False, 'error_message': 'Invalid session ID'})
    
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    zip_file = f"{session_download_dir}.zip"
    shutil.make_archive(session_download_dir, 'zip', session_download_dir)
    return send_file(zip_file, as_attachment=True)

if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    app.run(debug=True)
