from django.contrib import admin
from .models import Employee, Assignment, Attendance, Progress

# Register your models here.
admin.site.register(Employee)
admin.site.register(Assignment)
admin.site.register(Attendance)
admin.site.register(Progress)

