from flask import Flask, render_template, request, jsonify
from zxcvbn import zxcvbn
import subprocess
import os
import math
import traceback

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def format_crack_time(seconds):
    if seconds is None or seconds > 3.1536e16:
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

        # Run Java program for basic character flags & length
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

        has_lower = lines[2].lower() == 'true'
        has_upper = lines[3].lower() == 'true'
        has_digit = lines[4].lower() == 'true'
        has_symbol = lines[5].lower() == 'true'
        length = int(lines[6])

        # --- SMART PATTERN & DICTIONARY LOGIC (ZXCVBN) ---
        zx_result = zxcvbn(password)
        
        # zx_result['score'] is 0 to 4. Map it to a 0-100 score.
        score = zx_result['score'] * 25
        if score > 100: 
            score = 100

        # Calculate realistic entropy derived from zxcvbn's guesses
        guesses = zx_result.get('guesses', 1)
        entropy = math.log2(guesses) if guesses > 0 else 0.0

        crack_times = zx_result.get('crack_times_seconds', {})
        formatted_crack_times = {
            "online": format_crack_time(crack_times.get('online_throttling_100_per_hour')),
            "cpu": format_crack_time(crack_times.get('offline_slow_hashing_1e4_per_second')),
            "gpu": format_crack_time(crack_times.get('offline_fast_hashing_1e10_per_second'))
        }

        # Collect smart feedback warnings & suggestions
        feedback = zx_result.get('feedback', {})
        warnings = []
        if feedback.get('warning'):
            warnings.append(f"⚠️ {feedback['warning']}")
        for suggestion in feedback.get('suggestions', []):
            warnings.append(f"💡 {suggestion}")

        result = {
            "score": score,
            "entropy": round(entropy, 2),
            "hasLower": has_lower,
            "hasUpper": has_upper,
            "hasDigit": has_digit,
            "hasSymbol": has_symbol,
            "length": length,
            "crackTimes": formatted_crack_times,
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
