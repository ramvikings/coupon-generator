from flask import Flask, send_file, render_template_string, request, redirect, url_for
import pandas as pd
import random
import string
import os
from threading import Thread

app = Flask(__name__)
EXCEL_FILE = "coupons.xlsx"

# ------------------- Coupon logic -------------------
def generate_random_coupon(prefix="GU09", length=10):
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choices(chars, k=length))
    return prefix + random_str

# ------------------- HTML -------------------
HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>Coupon Generator</title>
</head>
<body>
    <h1>Generate Random Coupons</h1>
    <form action="/generate" method="post">
        <label>Number of Coupons:</label>
        <input type="number" name="num_coupons" min="1" value="100" required>
        <button type="submit">Run Code</button>
    </form>
    {% if file_ready %}
    <br><br>
    <a href="{{ url_for('download') }}">
        <button>Download Excel</button>
    </a>
    {% endif %}
</body>
</html>
"""

# ------------------- Routes -------------------
@app.route("/")
def index():
    file_ready = os.path.exists(EXCEL_FILE)
    return render_template_string(HTML_PAGE, file_ready=file_ready)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        num_coupons = int(request.form.get("num_coupons", 100))
    except ValueError:
        num_coupons = 100

    coupons = set()
    while len(coupons) < num_coupons:
        coupons.add(generate_random_coupon())

    df = pd.DataFrame(list(coupons), columns=["Coupon"])
    df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    
    return redirect(url_for('index'))

@app.route("/download")
def download():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE,
                         download_name="coupons.xlsx",
                         as_attachment=True)
    return "File not found. Please generate coupons first."

# ------------------- Run Flask in background -------------------
def run_app():
    app.run(debug=False, use_reloader=False)

# Start Flask server in a separate thread
thread = Thread(target=run_app)
thread.start()
