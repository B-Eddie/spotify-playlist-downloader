from flask import Flask, request, render_template, send_file, jsonify
import subprocess
import os
import shutil
import uuid
import imageio_ffmpeg as ffmpeg
import threading
import time

app = Flask(__name__)
DOWNLOAD_DIR = './downloads'

def createid():
    session_id = str(uuid.uuid4())
    return session_id

def download_song(id):
    song_url = request.form['song_url']
    
    session_download_dir = os.path.join(DOWNLOAD_DIR, id)
    
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
            return jsonify({'success': True, 'session_id': id})
        else:
            return jsonify({'success': False, 'error_message': f"Error: {result.stderr}"})
    except Exception as e:
        return jsonify({'success': False, 'error_message': f"Unexpected error: {str(e)}"})


def download_progress(session_id):
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    
    try:
        # progress based on downloaded and total items
        total_items = len(os.listdir(session_download_dir))
        downloaded_items = len([name for name in os.listdir(session_download_dir) if os.path.isfile(os.path.join(session_download_dir, name))])
        percentage = int((downloaded_items / total_items) * 100) if total_items > 0 else 0
        
        return jsonify({'percentage': percentage})
    except Exception as e:
        return jsonify({'percentage': 0})

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
            return jsonify({'success': True, 'session_id': session_id})
        else:
            return jsonify({'success': False, 'error_message': f"Error: {result.stderr}"})
    except Exception as e:
        return jsonify({'success': False, 'error_message': f"Unexpected error: {str(e)}"})

@app.route('/download_progress/<session_id>')
def download_progress(session_id):
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    
    try:
        # progress based on downloaded and total items
        total_items = len(os.listdir(session_download_dir))
        downloaded_items = len([name for name in os.listdir(session_download_dir) if os.path.isfile(os.path.join(session_download_dir, name))])
        percentage = int((downloaded_items / total_items) * 100) if total_items > 0 else 0
        
        return jsonify({'percentage': percentage})
    except Exception as e:
        return jsonify({'percentage': 0})

@app.route('/download_and_progress', methods=['POST'])
def download_and_progress():
    session_id = createid()
    
    downloadSong = threading.Thread(target=download_song, args=(session_id,))
    downloadProgress = threading.Thread(target=download_progress, args=(session_id,))
    
    downloadSong.start()
    downloadProgress.start()
    
    downloadSong.join()
    downloadProgress.join()
    
    # process has started
    return jsonify({'success': True, 'message': 'Download and progress tracking started'})

@app.route('/download_zip/<session_id>')
def download_zip(session_id):
    session_download_dir = os.path.join(DOWNLOAD_DIR, session_id)
    zip_file = f"{session_download_dir}.zip"
    shutil.make_archive(session_download_dir, 'zip', session_download_dir)
    return send_file(zip_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
