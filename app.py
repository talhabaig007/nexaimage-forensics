from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
from config import Config
from utils.exif_analyzer import ExifAnalyzer
from utils.image_analyzer import ImageAnalyzer
from utils.hash_generator import HashGenerator
from utils.ocr_processor import OCRProcessor
from utils.report_generator import ReportGenerator
from utils.security_analyzer import SecurityAnalyzer

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')

@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file format'}), 400
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Analyze image
        exif_analyzer = ExifAnalyzer(filepath)
        image_analyzer = ImageAnalyzer(filepath)
        hash_generator = HashGenerator(filepath)
        ocr_processor = OCRProcessor(filepath)
        security_analyzer = SecurityAnalyzer(filepath)
        
        # Gather all analysis results
        results = {
            'file_info': {
                'filename': original_filename,
                'extension': extension,
                'size': os.path.getsize(filepath),
                'size_formatted': format_size(os.path.getsize(filepath))
            },
            'image_info': image_analyzer.get_basic_info(),
            'exif_data': exif_analyzer.get_all_exif(),
            'gps_data': exif_analyzer.get_gps_data(),
            'metadata_summary': exif_analyzer.get_metadata_summary(),
            'hashes': hash_generator.get_all_hashes(),
            'image_analysis': image_analyzer.analyze_image(),
            'ocr_text': ocr_processor.extract_text(),
            'security_analysis': security_analyzer.analyze(),
            'analysis_id': str(uuid.uuid4()),
            'analysis_date': datetime.now().isoformat()
        }
        
        # Store in session for report generation
        session['last_analysis'] = results
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        report_gen = ReportGenerator(data)
        report_path = report_gen.generate()
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f"forensic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/about')
def about():
    return render_template('about.html')

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)