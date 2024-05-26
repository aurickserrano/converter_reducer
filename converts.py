from flask import Blueprint, request, jsonify, send_file, render_template, url_for, redirect
from werkzeug.utils import secure_filename
import subprocess
import os
import requests

convert_bp = Blueprint('convert', __name__)
LOG_SERVICE_URL = 'http://log_service:5002/log'
LOG_TOKEN = 'logsecrettoken'

def verify_token(token):
    return token == 'secrettoken'

def log_action(service, action, status, error=None):
    log_data = {
        'service': service,
        'action': action,
        'status': status,
        'token': LOG_TOKEN,
        'error': error
    }
    try:
        requests.post(LOG_SERVICE_URL, json=log_data)
    except Exception as e:
        print(f"Failed to log action: {e}")

@convert_bp.route('/convert_to_txt', methods=['POST'])
def convert_to_txt():
    try:
        token = request.form.get('token')
        if not verify_token(token):
            log_action('convert_to_txt', 'Unauthorized', 'Failed')
            return jsonify({'error': 'Unauthorized'}), 401

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join('/tmp/uploads', filename)
            file.save(filepath)
            output_filepath = f"{filepath}.txt"

            try:
                subprocess.run(['pdftotext', filepath, output_filepath], check=True)
                log_action('convert_to_txt', 'Success', 'Success')
                download_url = url_for('convert.download_file', filename=os.path.basename(output_filepath))
                return render_template('result.html', download_url=download_url)
            except subprocess.CalledProcessError as e:
                log_action('convert_to_txt', 'Conversion', 'Failed', str(e))
                return jsonify({'error': 'Conversion failed'}), 500
        else:
            return jsonify({'error': 'Invalid file format'}), 400
    except Exception as e:
        log_action('convert_to_txt', 'Exception', 'Failed', str(e))
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@convert_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join('/tmp/uploads', filename), as_attachment=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}
