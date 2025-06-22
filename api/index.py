from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return {"status": "ok", "message": "SubscriptionPro API - Fixed Version"}

@app.route('/health')
def health():
    supabase_url = os.environ.get('SUPABASE_URL', 'NOT_SET')
    return {
        "status": "ok", 
        "message": "SubscriptionPro API", 
        "supabase_configured": "YES" if supabase_url != 'NOT_SET' else "NO",
        "env_check": supabase_url[:20] + "..." if supabase_url != 'NOT_SET' else "NOT_SET"
    }

@app.route('/users')
def users():
    return jsonify([{"id": "1", "email": "REAL_DATA_COMING_SOON", "name": "Admin"}])

if __name__ == '__main__':
    app.run()