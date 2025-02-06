import os
import sys

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delegation.settings') # Replace 'delegation' with your project name
django.setup()

from tasks.models import Progress
from django.db.models import Count

duplicates = Progress.objects.values('assignment', 'date').annotate(count=Count('id')).filter(count__gt=1)

for duplicate in duplicates:
    progress_objects = Progress.objects.filter(assignment=duplicate['assignment'], date=duplicate['date']).order_by('id')  # Order by ID for consistency

    # Keep the first record and delete the rest
    main_progress = progress_objects.first()
    for progress_object in progress_objects[1:]:  # Iterate from the second record
        print(f"Deleting duplicate Progress: {progress_object}") # Print which records are being deleted
        progress_object.delete()

print("Duplicate Progress records cleaned up.")