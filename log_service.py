from flask import Flask, request, jsonify
import logging
import os

app = Flask(__name__)
log_directory = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, 'log_service.log')
app.config['LOG_FILE'] = log_file
app.config['TOKEN'] = 'logsecrettoken'

logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.INFO)

def log_action_local(service, action, status, token, error=None):
    if token != app.config['TOKEN']:
        logging.error(f"Unauthorized access attempt with token: {token}")
        return jsonify({'error': 'Unauthorized'}), 401
    if error:
        logging.error(f"Service: {service}, Action: {action}, Status: {status}, Error: {error}")
    else:
        logging.info(f"Service: {service}, Action: {action}, Status: {status}")
    return jsonify({'status': 'logged'}), 200

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    service = data.get('service')
    action = data.get('action')
    status = data.get('status')
    token = data.get('token')
    error = data.get('error')
    return log_action_local(service, action, status, token, error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
