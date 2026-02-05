import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timmy_gym_demo.settings')

django.setup()

# Run migrations on cold start for serverless
try:
	from django.core.management import call_command
	call_command('migrate', interactive=False, run_syncdb=True, verbosity=0)
except Exception:
	# Avoid crashing the function on migration errors
	pass

app = get_wsgi_application()
