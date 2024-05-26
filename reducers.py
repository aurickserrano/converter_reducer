from flask import Blueprint, request, jsonify, send_file, render_template, url_for, redirect
from werkzeug.utils import secure_filename
import subprocess
import os
import requests

reducer_bp = Blueprint('reducer', __name__)
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

@reducer_bp.route('/reduce_resolution', methods=['POST'])
def reduce_resolution():
    try:
        token = request.form.get('token')
        if not verify_token(token):
            log_action('reduce_resolution', 'Unauthorized', 'Failed')
            return jsonify({'error': 'Unauthorized'}), 401

        if 'file' not in request.files:
            log_action('reduce_resolution', 'No file part', 'Failed')
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        resolution = request.form.get('resolution')
        if file.filename == '' or not resolution:
            log_action('reduce_resolution', 'No selected file or resolution', 'Failed')
            return jsonify({'error': 'No selected file or resolution'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join('/tmp/uploads', filename)
            file.save(filepath)
            output_filepath = f"{os.path.splitext(filepath)[0]}_reduced.pdf"

            try:
                result = subprocess.run(
                    ['gs', '-sDEVICE=pdfwrite', f'-dPDFSETTINGS=/{resolution}', '-o', output_filepath, filepath],
                    check=True, capture_output=True
                )
                log_action('reduce_resolution', 'Success', 'Success', result.stdout.decode())
                download_url = url_for('reducer.download_file', filename=os.path.basename(output_filepath))
                return render_template('result.html', download_url=download_url)
            except subprocess.CalledProcessError as e:
                log_action('reduce_resolution', 'Reduction', 'Failed', e.stderr.decode())
                return jsonify({'error': 'Reduction failed', 'message': e.stderr.decode()}), 500
        else:
            log_action('reduce_resolution', 'Invalid file format', 'Failed')
            return jsonify({'error': 'Invalid file format'}), 400
    except Exception as e:
        log_action('reduce_resolution', 'Exception', 'Failed', str(e))
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@reducer_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join('/tmp/uploads', filename), as_attachment=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}
