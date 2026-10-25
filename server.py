from flask import Flask, render_template, request, jsonify
import subprocess
import os
import math
import re
import traceback

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def format_crack_time(seconds):
    if math.isinf(seconds) or seconds > 3.1536e16:
        return "Billions of years"
    if seconds < 1:
        return "Instant"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours"
    elif seconds < 31536000:
        return f"{int(seconds / 86400)} days"
    elif seconds < 31536000 * 1000:
        return f"{int(seconds / 31536000)} years"
    else:
        return f"{int(seconds / (31536000 * 1000))} thousand+ years"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        password = data.get("password", "")

        process = subprocess.Popen(
            ["java", "EntropyTest"],
            cwd=BASE_DIR,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=password + "\n")
        
        if process.returncode != 0:
            return jsonify({"error": "Java process exited with error", "stderr": stderr}), 500

        lines = [line.strip() for line in stdout.strip().split("\n") if line.strip()]
        if len(lines) < 7:
            return jsonify({"error": "Invalid output length from Java program", "stdout": stdout}), 500

        score = int(lines[0])
        entropy = float(lines[1])
        
        # Default crack time calculation
        try:
            combinations = math.pow(2, max(0, entropy - 1))
        except OverflowError:
            combinations = float('inf')

        speeds = {"online": 1e3, "cpu": 1e7, "gpu": 1e11}
        crack_times = {
            "online": format_crack_time(combinations / speeds["online"]),
            "cpu": format_crack_time(combinations / speeds["cpu"]),
            "gpu": format_crack_time(combinations / speeds["gpu"])
        }

        # --- SPECIALIZED TESTS / HEURISTICS ---
        warnings = []

        # 1. Email ID Detection Test
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(email_pattern, password):
            warnings.append("⚠️ Warning: This password matches an email address format!")
            score = max(5, score - 65)
            crack_times = {"online": "Instant", "cpu": "Instant", "gpu": "Instant"}

        # 2. Repeating Characters Test (e.g., aaaaaaa, 111111)
        if len(set(password)) == 1 and len(password) > 2:
            warnings.append("⚠️ Warning: Password consists of entirely repeating characters!")
            score = 5
            crack_times = {"online": "Instant", "cpu": "Instant", "gpu": "Instant"}

        # 3. Common sequential / keyboard patterns check
        common_sequences = ["123456", "password", "qwerty", "admin", "welcome", "letmein"]
        if password.lower() in common_sequences:
            warnings.append("⚠️ Warning: This is a heavily used common password!")
            score = 5
            crack_times = {"online": "Instant", "cpu": "Instant", "gpu": "Instant"}

        result = {
            "score": score,
            "entropy": entropy,
            "hasLower": lines[2].lower() == 'true',
            "hasUpper": lines[3].lower() == 'true',
            "hasDigit": lines[4].lower() == 'true',
            "hasSymbol": lines[5].lower() == 'true',
            "length": int(lines[6]),
            "crackTimes": crack_times,
            "warnings": warnings
        }
        return jsonify(result)

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"error": str(e), "traceback": tb}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
