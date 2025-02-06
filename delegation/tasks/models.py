from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Assignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='assignments') # Forward reference and related name
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_assignments') # Added created_by

    def __str__(self):
        return f"{self.employee.user.username} - {self.title} - {self.status}"



class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')], default='absent')

    class Meta:
        unique_together = ('employee', 'date')  

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.status}"
    
class Progress(models.Model):
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)  # Or auto_now_add=True if you want it set only on creation
    percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0  # Set a default value
    )
    details = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('assignment', 'date')  # Ensure one record per assignment per day

    def __str__(self):
        return f"Progress for {self.assignment} on {self.date}"
