from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import os
import uuid
import logging
from modules import process_video_task
from modules.waveform_generation import generate_waveform

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    use_simple = request.form.get('use_simple', 'false').lower() == 'true'
    
    if file:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Generate waveform for original audio
        original_waveform = generate_waveform(filepath)
        
        return jsonify({ 'original_waveform': original_waveform }), 202
        
@app.route('/process/<user_id>/<name>', methods=['POST'])
def process_file(user_id, name):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    use_simple = request.form.get('use_simple', 'false').lower() == 'true'
    
    if file:
        filename = str(uuid.uuid4()) + '_' + user_id + '_' + name
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Start async task
        task = process_video_task.delay(filepath, PROCESSED_FOLDER, use_simple)
        
        print(f"Task created with ID: {task.id}, using simple method: {use_simple}")
        
        return jsonify({ 'task_id': task.id }), 202

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    
    task = process_video_task.AsyncResult(task_id)
    logger.info(f"task from status endpoint: {task}")
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is waiting for execution'
        }
    elif task.state != 'FAILURE':
        response = {
            'result': task.info if task.info else 'Still waiting on result',
            'state': task.state,
            'status': 'Task is in progress' if task.state == 'PROCESSING' else 'Task completed'
        }
    else:
        response = {
            'state': task.state,
            'status': 'Task failed',
            'error': str(task.info)
        }
    return jsonify(response)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        
        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
                logger.info(f"File deleted after download: {file_path}")
            except Exception as error:
                logger.exception(f"Error removing file: {error}")
            return response

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.exception(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'Error downloading file'}), 500
    
@app.route('/user_videos/<user_id>', methods=['GET'])
def user_videos(user_id):
    user_videos = []
    for filename in os.listdir(PROCESSED_FOLDER):
        if filename.startswith(f"{user_id}_"):
            video_path = os.path.join(PROCESSED_FOLDER, filename)
            video_size = os.path.getsize(video_path)
            video_info = {
                "filename": filename,
                "size": video_size,
                "url": f"/download/{filename}"
            }
            user_videos.append(video_info)
    
    return jsonify({"videos": user_videos})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')