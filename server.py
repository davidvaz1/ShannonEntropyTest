from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Compile Java file on startup
os.system("javac EntropyTest.java")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    password = data.get("password", "")

    try:
        # Run Java program and pass password via stdin
        process = subprocess.Popen(
            ["java", "EntropyTest"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=password + "\n")
        
        if process.returncode != 0:
            return jsonify({"error": stderr}), 500

        lines = stdout.strip().split("\n")
        if len(lines) < 7:
            return jsonify({"error": "Invalid output from Java program"}), 500

        result = {
            "score": int(lines[0]),
            "entropy": float(lines[1]),
            "hasLower": lines[2].lower() == 'true',
            "hasUpper": lines[3].lower() == 'true',
            "hasDigit": lines[4].lower() == 'true',
            "hasSymbol": lines[5].lower() == 'true',
            "length": int(lines[6])
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
