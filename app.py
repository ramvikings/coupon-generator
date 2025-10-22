from flask import Flask, jsonify, request, render_template
import os

app = Flask(__name__)

# Required for Vercel - serve static files
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coupon Generator</title>
    </head>
    <body>
        <h1>Coupon Generator</h1>
        <p>Server is running!</p>
        <form action="/generate" method="POST">
            <button type="submit">Generate Coupon</button>
        </form>
    </body>
    </html>
    """

@app.route('/generate', methods=['POST'])
def generate_coupon():
    # Simple coupon generation logic
    import random
    import string
    coupon = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return jsonify({"coupon": coupon, "status": "success"})

# Vercel requires this specific variable name
if __name__ == '__main__':
    app.run(debug=True)
else:
    # This is required for Vercel serverless functions
    application = app
