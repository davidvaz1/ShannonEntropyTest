from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    password = data.get("password", "")

    try:
        # Run the pre-compiled Java program
        process = subprocess.Popen(
            ["java", "-cp", ".", "EntropyTest"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=password + "\n")
        
        if process.returncode != 0:
            print(f"Java execution error: {stderr}")
            return jsonify({"error": stderr}), 500

        # Filter out empty lines just in case
        lines = [line.strip() for line in stdout.strip().split("\n") if line.strip()]
        if len(lines) < 7:
            print(f"Unexpected Java output: {stdout}")
            return jsonify({"error": "Invalid output from Java program", "output": stdout}), 500

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
        print(f"Server exception: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
