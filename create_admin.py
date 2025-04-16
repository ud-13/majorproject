import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tenant.settings')
django.setup()

from Tenant.models import User

# Create superuser
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        role='admin'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')