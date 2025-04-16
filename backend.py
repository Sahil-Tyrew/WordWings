from flask import Flask, request, jsonify
#Install - pip install flask-cors
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from wordwings import simplify_text, simplify_text_with_ai, chunk_text, image_to_text

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/simplify', methods=['POST'])
def simplify():
    data = request.get_json() or {}
    text = data.get('text', '')
    use_ai = data.get('use_ai', False)
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if use_ai:
        simplified = simplify_text_with_ai(text)
    else:
        simplified = simplify_text(text)
    
    return jsonify({'simplified': simplified})

@app.route('/chunk', methods=['POST'])
def chunk():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    chunked = chunk_text(text)
    return jsonify({'chunked': chunked})

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    extracted = image_to_text(filepath)
    
    try:
        os.remove(filepath)
    except OSError as e:
        app.logger.error("Error deleting file: %s", e)
    
    return jsonify({'extracted': extracted})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
