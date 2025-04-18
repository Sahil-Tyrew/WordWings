from flask import Flask, request, jsonify
#Install - pip install flask-cors
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from wordwings_core import simplify_text, simplify_text_with_ai, chunk_text, image_to_text

print(">>> backend.py starting up")


app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


#for testing on basic connectivity 
@app.route('/ping', methods=['GET'])
def ping():
    print(">>> /ping called")
    return jsonify({'pong': True})


@app.route('/simplify', methods=['POST'])
def simplify():
    data = request.get_json() or {}
    text = data.get('text', '')
    use_ai = data.get('use_ai', False)
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        simplified = ( simplify_text_with_ai(text)
                       if data.get('use_ai') else
                       simplify_text(text) )
        return jsonify({'simplified': simplified})
    except Exception as e:
        app.logger.exception("Error processing /simplify")
        return jsonify({'error': 'Server error during simplification'}), 500

@app.route('/chunk', methods=['POST'])
def chunk():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    try:
        chunked = chunk_text(text)
        return jsonify({'chunked': chunked})
    except Exception as e:
        #real error for your debugging
        app.logger.exception("Error processing /chunk")
        # Return a JSON error so the extension can handle it
        return jsonify({'error': 'Server error during chunking'}), 500

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




