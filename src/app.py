"""
Flask Web Application for Animal Detection
Upload images and detect animals through a web interface
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import cv2
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from detector import AnimalDetector

app = Flask(__name__,
            template_folder=str(Path(__file__).parent.parent / 'templates'),
            static_folder=str(Path(__file__).parent.parent / 'static'))

# Configuration
UPLOAD_FOLDER = Path(__file__).parent.parent / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize detector
detector = AnimalDetector()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and detection"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))

        try:
            # Detect animals
            result_image, detections = detector.detect_animals(str(filepath))

            # Save result image
            result_filename = f"result_{filename}"
            result_filepath = Path(app.config['UPLOAD_FOLDER']) / result_filename
            cv2.imwrite(str(result_filepath), result_image)

            # Prepare response
            summary = detector.get_detection_summary(detections)

            return jsonify({
                'success': True,
                'summary': summary,
                'detections': detections,
                'original_image': url_for('uploaded_file', filename=filename),
                'result_image': url_for('uploaded_file', filename=result_filename)
            })

        except Exception as e:
            return jsonify({'error': f'Detection failed: {str(e)}'}), 500

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'animal-detection'})


@app.route('/api/info')
def info():
    """API information"""
    return jsonify({
        'name': 'Animal Detection API',
        'version': '1.0.0',
        'supported_animals': list(AnimalDetector.CORE_ANIMALS),
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024),
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })


if __name__ == '__main__':
    # Ensure upload folder exists
    UPLOAD_FOLDER.mkdir(exist_ok=True)

    # Run the app
    print("\n" + "=" * 60)
    print("🐾 Animal Detection Web App")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("\nPress CTRL+C to stop the server\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
