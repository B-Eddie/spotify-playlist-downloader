from flask import Flask, request, render_template, send_file, jsonify, redirect, after_this_request, url_for
import subprocess
import os
import shutil
import uuid
import imageio_ffmpeg as ffmpeg
import threading
import time

app = Flask(__name__)
DOWNLOAD_DIR = './downloads'

# Store session data in a dictionary
sessions = {}

# del session directory
def cleanup_session(session_id):
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    session_download_zip = os.path.join(DOWNLOAD_DIR, session_id + ".zip")
    if os.path.exists(session_download_dir):
        shutil.rmtree(session_download_dir)
    
    if os.path.exists(session_download_zip):
        os.remove(session_download_zip)


def remove_sessions():
    global sessions
    sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_song():
    remove_sessions()
    song_url = request.form['song_url']
    session_id = str(uuid.uuid4())
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    sessions[session_id] = {'status': 'started', 'progress': 0}

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
        else:
            return jsonify({'success': False, 'error_message': f"Error: {result.stderr}"})
    except Exception as e:
        return jsonify({'success': False, 'error_message': f"Unexpected error: {str(e)}"})

@app.route('/download_zip/<session_id>')
def download_zip(session_id):
    if session_id not in sessions:
        return jsonify({'success': False, 'error_message': 'Invalid session ID'})
    
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    zip_file = f"{session_download_dir}.zip"
    shutil.make_archive(session_download_dir, 'zip', session_download_dir)
    
    #deletes directory
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    if os.path.exists(session_download_dir):
        shutil.rmtree(session_download_dir)
    return send_file(zip_file, as_attachment=True)


# seperate thing
@app.route('/get_id', methods=['GET'])
def get_id():
    time.sleep(1)
    session_key = list(sessions.keys())
    key = session_key[0]
    if len(session_key) != 1:
        print("yo waht")
        print(session_key)
    if key in sessions:
        return jsonify({'success': True, 'session_id': session_key, 'session_data': sessions})
    return jsonify({'success': False, 'error_message': 'Invalid session ID'})

@app.route('/download_progress/<session_id>')
def download_progress(session_id):
    if session_id not in sessions:
        return jsonify({'success': False, 'error_message': 'Invalid session ID'})
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    try:
        total_items = len(os.listdir(session_download_dir))
        
        session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
        exists = "False"
        if os.path.exists(session_download_dir):
            exists = "True"
        return jsonify({'success': "True", 'total_items': total_items, 'path_exists': exists})
    except Exception as e:
        return jsonify({'success': "False", 'error_message': str(e)})


if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    app.run(host='0.0.0.0', port=8080)
