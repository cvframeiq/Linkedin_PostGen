
# ====================== 📦 Import Libraries ======================

from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import os

# ====================== ⚙️ Import Custom Modules ======================
from Generator import generate_post  # Function to generate post content using image and prompt
from userinfo import get_linkedin_user_info, post_image_to_linkedin  # LinkedIn API integration

# ====================== 📁 Define Folder Paths ======================
# Define paths for template and static folders relative to this file's location
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Frontend/templates"))
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Frontend/static"))
UPLOAD_FOLDER = os.path.join(STATIC_DIR, "uploads")  # Where uploaded images will be saved

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ====================== 🚀 Initialize Flask App ======================
# Pass in the correct template and static folder locations
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Configure Flask to use the uploads folder

# ====================== 🌐 Define Route ======================
@app.route("/", methods=["GET", "POST"])
def index():
    generated_post = ""  # Store the caption
    image_url = None     # Path to preview image in UI
    error = None         # Error message, if any

    # Handle POST request (form submission)
    if request.method == "POST":
        # Get data from form
        access_token = request.form.get("access_token", "").strip()
        prompt = request.form.get("prompt", "").strip()

        # If access token is missing
        if not access_token:
            error = "❌ Please enter a valid LinkedIn Access Token."
            return render_template("index.html", error=error)

        # Try to get LinkedIn user info
        try:
            user_info = get_linkedin_user_info(access_token)
            person_urn = "urn:li:person:" + user_info["sub"]  # e.g., urn:li:person:abc123
        except Exception as e:
            error = f"⚠️ Error fetching user info: {e}"
            return render_template("index.html", error=error)

        # Handle image upload
        image = request.files.get("image")
        if image and image.filename:
            filename = secure_filename(image.filename)  # Clean filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Full server path
            image.save(image_path)  # Save uploaded file to disk
            image_url = url_for("static", filename=f"uploads/{filename}")  # Web path for preview
        else:
            image_path = ""  # No image uploaded

        # Generate post caption using prompt and image
        generated_post = generate_post(prompt, image_path)

        # Try posting to LinkedIn
        try:
            post_image_to_linkedin(access_token, person_urn, image_path, generated_post)
        except Exception as e:
            error = f"⚠️ Failed to post on LinkedIn: {e}"

    # Render the form and display results/errors if any
    return render_template("index.html", generated_post=generated_post, image_url=image_url, error=error)

# ====================== ▶️ Run the App ======================
if __name__ == "__main__":
    app.run(debug=True)
