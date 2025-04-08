from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

WEBHOOK_SECRET = 'your-secret-token-here'

REPO_DIR = '/path/to/your/repo'  

def pull_changes():
    try:
        result = subprocess.run(['git', 'pull'], check=True, capture_output=True, text=True, cwd=REPO_DIR)
        
        print("Git pull output:", result.stdout)
        print("Git pull error:", result.stderr)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Error pulling changes: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return e.stdout, e.stderr

@app.route('/webhook', methods=['POST'])
def webhook():
    token = request.headers.get('X-Webhook-Token')

    if token != WEBHOOK_SECRET:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json

    if data:
        status = data.get('status')
        message = data.get('message')
        commit = data.get('commit')
        branch = data.get('branch')
        artifact = data.get('artifact')

        print('Webhook received!')
        print(f"Status: {status}")
        print(f"Message: {message}")
        print(f"Commit: {commit}")
        print(f"Branch: {branch}")
        print(f"Artifact: {artifact}")

        if status == 'success':
            print('Triggering git pull...')
            output, error = pull_changes()
            
            if error:
                return jsonify({"message": "Failed to pull changes", "error": error}), 500
            else:
                return jsonify({"message": "Webhook received and changes pulled successfully", "output": output}), 200
        else:
            return jsonify({"message": "Build was not successful, skipping pull."}), 200

    else:
        return jsonify({"message": "Invalid webhook payload"}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
