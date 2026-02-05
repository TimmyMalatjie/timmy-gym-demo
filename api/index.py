import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timmy_gym_demo.settings')
django.setup()

app = get_wsgi_application()

def handler(request):
    """Handle incoming requests for Vercel"""
    return app(request.environ, request.start_response)
