from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import load_dotenv
import os
from openai import OpenAI

import cloudinary
import cloudinary.uploader

# Load environment variables
load_dotenv()

# Configure Cloudinary with your credentials
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

# Initialize Flask and OpenAI client
app = Flask(__name__)
CORS(app)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Allowed file extensions
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
        try:
            # Upload image to Cloudinary
            upload_result = cloudinary.uploader.upload(file)
            file_url = upload_result.get('secure_url')  # Get the Cloudinary-hosted URL
            print("FILE URL:", file_url)

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "You are an expert car analyst who can identify the make and model from an image. REFUSE EVERY OTHER REQUEST AS 'Invalid request'. RETURN ONLY THE MAKE, MODEL, AND YEAR. IF UNSURE, MAKE A GUESS, BUT DO RETURN AN ANSWER."},
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
            print("ERROR: ", e)
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400

@app.route('/health', methods=['GET'])
def health_check():
    """Check if the server is running."""
    return jsonify({"status": "Server is running"}), 200

if __name__ == '__main__':
    app.run()
