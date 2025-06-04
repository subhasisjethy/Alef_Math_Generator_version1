# app.py (modify only the index route to pass example_images)
import os
import base64
import asyncio
import json
from flask import Flask, render_template, request, jsonify, url_for
from dotenv import load_dotenv
from api_agno import call_async_api  # Import the async function

load_dotenv()

app = Flask(__name__)
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "a_default_secret_key_if_not_set")

# --- Routes ---

@app.route('/')
def index():
    """
    Renders the main HTML page, passing a list of filenames in static/examples
    so that the template can display clickable thumbnails.
    """
    example_images = []
    # Locate the 'static/examples' folder
    examples_dir = os.path.join(app.static_folder, 'examples')
    if os.path.exists(examples_dir):
        for fname in os.listdir(examples_dir):
            # Only include common image extensions
            if os.path.isfile(os.path.join(examples_dir, fname)) and \
               fname.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                example_images.append(fname)
    return render_template('index.html', example_images=example_images)

@app.route('/generate', methods=['POST'])
async def generate_questions():
    """
    Handles the asynchronous generation of questions based on form input.
    Expects 'num_questions', 'inputType', and potentially 'file' or 'text'.
    """
    try:
        num_questions = int(request.form.get('num_questions', 1))
        input_type = request.form.get('inputType')
        input_data = None
        is_image = False
        api_provider = 'openai'  # Default provider

        print(f"Received request: type={input_type}, num_questions={num_questions}")  # Debug

        if input_type == 'image' or input_type == 'pdf':
            file = request.files.get('file')
            if not file or not file.filename:
                return jsonify({"error": "No file uploaded."}), 400
            if not allowed_file(file.filename, input_type):
                return jsonify({"error": f"Invalid file type for {input_type} upload."}), 400

            # Read file content and encode to base64
            file_content = file.read()
            input_data = base64.b64encode(file_content).decode('utf-8')
            is_image = True
            print(f"Processing uploaded file: {file.filename}")

        elif input_type == 'text':
            input_data = request.form.get('text_input')
            if not input_data:
                return jsonify({"error": "No text provided."}), 400
            is_image = False
            print("Processing text input.")

        else:
            return jsonify({"error": "Invalid input type specified."}), 400

        # Create async tasks for the API calls
        tasks = []
        for _ in range(num_questions):
            tasks.append(asyncio.to_thread(call_async_api, 'a', input_data, is_image))

        # Run tasks concurrently and gather results
        print(f"Starting {len(tasks)} async API calls...")  # Debug
        results = await asyncio.gather(*tasks)
        print(f"Finished API calls. Results count: {len(results)}")  # Debug

        # Check for errors in results
        successful_results = [res for res in results if 'error' not in res]
        errors = [res['error'] for res in results if 'error' in res]

        if not successful_results and errors:
            return jsonify({"error": f"All API calls failed. First error: {errors[0]}"}), 500
        elif errors:
            print(f"Partial failure: {len(errors)} API calls failed.")

        print(successful_results)
        return jsonify({"results": successful_results})

    except Exception as e:
        print(f"Error in /generate endpoint: {str(e)}")
        if isinstance(e, ValueError):
            return jsonify({"error": f"Invalid input: {str(e)}"}), 400
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# --- Helper Functions ---

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg'}
ALLOWED_EXTENSIONS_PDF = {'pdf'}

def allowed_file(filename, input_type):
    """Checks if the file extension is allowed."""
    allowed_set = set()
    if input_type == 'image':
        allowed_set = ALLOWED_EXTENSIONS_IMG
    elif input_type == 'pdf':
        allowed_set = ALLOWED_EXTENSIONS_PDF

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_set


# --- Run Application ---

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
