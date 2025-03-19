import os
import requests
from dotenv import load_dotenv

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the user's home directory
HOME_DIR = os.path.expanduser("~")
# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FILE_TO_UPLOAD = os.getenv("FILE_TO_UPLOAD", f"{HOME_DIR}/.config/zed/settings.json")
# Load environment variables from .env file in the script's directory
load_dotenv(os.path.join(script_dir, ".env"), override=True)

if not GITHUB_TOKEN:
    raise Exception(
        "GITHUB_TOKEN is not set. Please set it in your .env file or environment variables."
    )

GIST_ID_FILE = "gist_id.txt"
GITHUB_API_URL = "https://api.github.com/gists"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def create_gist():
    with open(FILE_TO_UPLOAD, "r") as f:
        content = f.read()
    data = {
        "description": "Automated update of file content",
        "public": False,
        "files": {os.path.basename(FILE_TO_UPLOAD): {"content": content}},
    }
    response = requests.post(GITHUB_API_URL, headers=headers, json=data)
    if response.status_code == 201:
        gist = response.json()
        gist_id = gist["id"]
        gist_url = gist["html_url"]
        with open(GIST_ID_FILE, "w") as f:
            f.write(gist_id)
        print("Created gist with id:", gist_id)
        print("Gist URL:", gist_url)
    else:
        print("Error creating gist:", response.status_code, response.text)


def update_gist(gist_id):
    with open(FILE_TO_UPLOAD, "r") as f:
        content = f.read()
    data = {"files": {os.path.basename(FILE_TO_UPLOAD): {"content": content}}}
    url = f"{GITHUB_API_URL}/{gist_id}"
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        gist_url = response.json()["html_url"]
        print("Updated gist", gist_id)
        print("Gist URL:", gist_url)
    else:
        print("Error updating gist:", response.status_code, response.text)


def main():
    if not os.path.exists(GIST_ID_FILE):
        create_gist()
    else:
        with open(GIST_ID_FILE, "r") as f:
            gist_id = f.read().strip()
        if gist_id:
            update_gist(gist_id)
        else:
            create_gist()


if __name__ == "__main__":
    main()
