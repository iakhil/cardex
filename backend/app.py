from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
# Initialize Flask and OpenAI client
app = Flask(__name__)
CORS(app)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if a file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle image upload, process with OpenAI, and return the result."""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Generate URL for the uploaded file
        file_url = f"{request.url_root}uploads/{filename}"

        # Call OpenAI API
        try:
            #test_file_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/2023_Nissan_Rogue_SV_in_Super_Black%2C_front_left.jpg/280px-2023_Nissan_Rogue_SV_in_Super_Black%2C_front_left.jpg"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "You are an expert car anayst who can identify the make and model from an image. REFUSE EVERY OTHER REQUEST AS 'Invalid request'. RETURN ONLY TH E MAKE, MODEL, AND YEAR. IF UNSURE, MAKE A GUESS, BUT DO RETURN AN ANSWER."},
                            {"type": "image_url", "image_url": {"url": file_url}},
                        ],
                    }
                ],
                max_tokens=300,
            )

            # Extract the response
            ai_response = response.choices[0].message.content
            return jsonify({"url": file_url, "description": ai_response})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400

@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    """Serve the uploaded file."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/health', methods=['GET'])
def health_check():
    """Check if the server is running."""
    return jsonify({"status": "Server is running"}), 200

if __name__ == '__main__':
    app.run()
