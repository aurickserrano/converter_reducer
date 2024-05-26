from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

from reducers import reducer_bp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['TOKEN'] = 'secrettoken'

# Registrar os blueprints
app.register_blueprint(reducer_bp, url_prefix='/reduce')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
