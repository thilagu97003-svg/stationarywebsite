import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_shop.settings')

application = get_wsgi_application()

# Vercel serverless environment auto-migrate & seed
if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        call_command('seed_data')
    except Exception as e:
        print("Migration error:", e)

app = application