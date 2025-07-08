import requests

# ===================== 🔍 Fetch LinkedIn User Info ===================== #
def get_linkedin_user_info(access_token):
    """
    Fetches the LinkedIn user information using the provided access token.
    Returns user info as a JSON object (contains 'sub', etc.).
    """
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}"  # Required for authentication
    }

    print("📡 Fetching LinkedIn user info...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("✅ User Info Received:")
        print(response.json())
        return response.json()
    else:
        # If token is invalid or expired
        print(f"❌ Failed to fetch user info. Status: {response.status_code}")
        print(response.text)
        raise Exception("Invalid or expired access token.")

# ===================== 📤 Post Image and Message to LinkedIn ===================== #
def post_image_to_linkedin(access_token, person_urn, image_path, message_text):
    """
    Posts an image and caption to the user's LinkedIn feed using their person_urn.
    This is a 3-step process:
    1. Register the image upload
    2. Upload the image to the URL received
    3. Create the post with uploaded image
    """
    # Step 1: Register image upload
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],  # Defines it's a feed image
            "owner": person_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    print("🔄 Registering image upload...")
    res = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=headers,
        json=register_body
    )

    if res.status_code != 200:
        print("❌ Upload registration failed:", res.text)
        return

    # Extract upload URL and asset URN
    upload_info = res.json()
    upload_url = upload_info["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = upload_info["value"]["asset"]
    print("✅ Upload URL received!")

    # Step 2: Upload image binary to the upload URL
    print("📤 Uploading image...")
    with open(image_path, "rb") as img_file:
        upload_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "image/jpeg"  # Adjust this if your image is PNG etc.
        }
        upload_res = requests.put(upload_url, headers=upload_headers, data=img_file)

    if upload_res.status_code not in [200, 201]:
        print("❌ Image upload failed:", upload_res.text)
        return

    print("✅ Image uploaded successfully!")

    # Step 3: Post the image and message to the user's feed
    post_body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": message_text  # The post caption/content
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": "This image was uploaded via LinkedIn API"
                        },
                        "media": asset,  # Asset URN from upload registration
                        "title": {
                            "text": "Python LinkedIn API Post"
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"  # Visibility scope
        }
    }

    print("📝 Publishing LinkedIn post...")
    final_post = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=headers,
        json=post_body
    )

    # Show result of post request
    print("📬 Post Status:", final_post.status_code)
    print("🔍 Response:", final_post.json())

# ===================== 🧪 Test Run in CLI ===================== #
if __name__ == "__main__":
    # Prompt user to enter access token
    access_token = input("🔐 Enter your LinkedIn access token: ").strip()

    try:
        # Step 1: Get user info and extract person URN
        user_info = get_linkedin_user_info(access_token)
        PERSON_URN = "urn:li:person:" + user_info['sub']
    except Exception as e:
        print("❌ Could not authenticate user:", e)
        exit()
