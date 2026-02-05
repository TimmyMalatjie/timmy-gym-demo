import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timmy_gym_demo.settings')
django.setup()

from django.core.wsgi import get_wsgi_application
from django.core.files.storage import staticfiles_storage

app = get_wsgi_application()

def handler(request, response):
    """Handle incoming requests for Vercel"""
    try:
        # Call the WSGI application
        app_iter = app(request['rawPath'], request['headers'], request['method'])
        return {
            'statusCode': 200,
            'body': ''.join([chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk for chunk in app_iter]),
            'headers': {'Content-Type': 'text/html'}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e),
            'headers': {'Content-Type': 'text/plain'}
        }
