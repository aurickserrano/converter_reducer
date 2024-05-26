from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

from converts import convert_bp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['TOKEN'] = 'secrettoken'

# Registrar os blueprints
app.register_blueprint(convert_bp, url_prefix='/convert')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
