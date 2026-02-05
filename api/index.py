import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timmy_gym_demo.settings')

app = get_wsgi_application()
