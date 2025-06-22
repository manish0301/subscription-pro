from flask import Flask

app = Flask(__name__)

def handler(request):
    return {
        "status": "ok",
        "message": "SubscriptionPro API Working!",
        "method": request.method if hasattr(request, 'method') else 'GET'
    }