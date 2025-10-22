from flask import Flask, jsonify, request, render_template, send_file
import os
import random
import string
import pandas as pd
from io import BytesIO
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coupon Generator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
            }
            .btn {
                background-color: #007bff;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-size: 18px;
                cursor: pointer;
                margin: 10px;
                text-decoration: none;
                display: inline-block;
            }
            .btn:hover {
                background-color: #0056b3;
            }
            .btn-download {
                background-color: #28a745;
            }
            .btn-download:hover {
                background-color: #1e7e34;
            }
            .hidden {
                display: none;
            }
            .coupon-list {
                text-align: left;
                margin: 20px 0;
                max-height: 200px;
                overflow-y: auto;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎫 Coupon Generator</h1>
            <p>Click the button below to generate coupon codes and download them as Excel file.</p>
            
            <button class="btn" onclick="generateCoupons()" id="runBtn">Run Code & Generate Coupons</button>
            
            <div id="loading" class="hidden">
                <p>⏳ Generating coupons... Please wait!</p>
            </div>
            
            <div id="downloadSection" class="hidden">
                <h3>✅ Coupons Generated Successfully!</h3>
                <div id="couponPreview" class="coupon-list"></div>
                <a href="/download" class="btn btn-download">📥 Download Excel File</a>
                <button class="btn" onclick="generateCoupons()">🔄 Generate New Coupons</button>
            </div>
        </div>

        <script>
            function generateCoupons() {
                // Show loading
                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('runBtn').disabled = true;
                document.getElementById('downloadSection').classList.add('hidden');
                
                fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Hide loading
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('runBtn').disabled = false;
                    
                    // Show download section
                    document.getElementById('downloadSection').classList.remove('hidden');
                    
                    // Show coupon preview
                    const couponList = document.getElementById('couponPreview');
                    couponList.innerHTML = '<strong>Generated Coupons Preview:</strong><br>';
                    data.coupons.forEach(coupon => {
                        couponList.innerHTML += `• ${coupon}<br>`;
                    });
                    couponList.innerHTML += `<br><strong>Total: ${data.coupons.length} coupons generated</strong>`;
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('runBtn').disabled = false;
                    alert('Error generating coupons. Please try again.');
                });
            }
        </script>
    </body>
    </html>
    """

@app.route('/generate', methods=['POST'])
def generate_coupon():
    try:
        # Generate multiple coupons (20 for example)
        coupons = []
        for i in range(20):
            coupon = 'CPN-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            coupons.append(coupon)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Coupon Code': coupons,
            'Generated Date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Status': 'Active'
        })
        
        # Save to BytesIO buffer (in memory)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Coupons', index=False)
        
        # Store the buffer in a global variable or session (for simplicity)
        app.config['EXCEL_BUFFER'] = buffer.getvalue()
        
        return jsonify({
            "status": "success", 
            "message": "Coupons generated successfully",
            "coupons": coupons,
            "count": len(coupons)
        })
    
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Error generating coupons: {str(e)}"
        }), 500

@app.route('/download')
def download_excel():
    try:
        buffer = app.config.get('EXCEL_BUFFER')
        if not buffer:
            return jsonify({"error": "No coupons generated yet"}), 400
        
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'coupons_{timestamp}.xlsx'
        
        return send_file(
            BytesIO(buffer),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({"error": f"Download error: {str(e)}"}), 500

# Vercel requires this specific variable name
if __name__ == '__main__':
    app.run(debug=True)
else:
    # This is required for Vercel serverless functions
    application = app
