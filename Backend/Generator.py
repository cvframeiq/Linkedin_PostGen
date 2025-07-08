import base64
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")  # Gemini API key loaded from environment


# ===================== 🧠 Generate LinkedIn Post ===================== #
def generate_post(prompt, image_path):
    """
    Sends a prompt and image to Google's Gemini model to generate
    a professional LinkedIn post caption.

    Parameters:
        prompt (str): Text description of the image or theme
        image_path (str): File path to the uploaded image

    Returns:
        str: Generated post caption, or an error message
    """

    # Handle empty or missing image
    if not image_path:
        return "[Error] No image provided."

    # Encode the image as base64
    try:
        with open(image_path, "rb") as f:
            base64_img = base64.b64encode(f.read()).decode("utf-8")  # Convert to base64 string
    except Exception as e:
        return f"[Error reading image] {e}"

    # === 🧠 Gemini API Endpoint ===
    endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-1.5-flash:generateContent?key=" + API_KEY
    )

    headers = {
        "Content-Type": "application/json"
    }

    # === 📝 Gemini Request Payload ===
    # The prompt guides the model to create a high-quality, clean LinkedIn post
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "You're a professional content writer crafting a single high-quality LinkedIn post. "
                            "Given the image and topic, write a detailed, thoughtful, motivational caption suitable for a LinkedIn post. "
                            "Make it sound natural, inspiring, and related to career, mindset, or growth. Don't add any markdown, have a clean plain text, emojis if needed. "
                            "Add 3–5 relevant hashtags. Return only the post text. No text before or after.\n\n"
                            f"Image context: {prompt}"  # User-provided prompt
                        )
                    },
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",  # You can adjust this if needed (e.g., image/png)
                            "data": base64_img  # Encoded image data
                        }
                    }
                ]
            }
        ]
    }

    # === 📡 Make Request to Gemini API ===
    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            # ✅ Successfully received generated content
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # ❌ API returned an error
            return f"[API Error {response.status_code}]\n{response.text}"

    except Exception as e:
        # ❌ Failed to connect to Gemini API
        return f"[Request Failed] {e}"
