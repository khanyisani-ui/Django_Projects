from django import forms
from .models import Assignment, User, Employee, Progress

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'deadline', 'employee', 'status']  # Include 'status'
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.") #username field
    password = forms.CharField(widget=forms.PasswordInput, required=True) #password field
    role = forms.ChoiceField(choices=Employee.ROLE_CHOICES, required=True) #role field


    class Meta:
        model = User # Model is now User
        fields = ['username', 'password', 'first_name', 'last_name', 'email'] # User fields
       

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.set_password(self.cleaned_data['password']) # Hash the password
        if commit:
            user.save()
        return user

class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['percentage', 'details'] 
        exclude = ('assignment', 'date')

class ProgressUpdateForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['percentage', 'details']

class UpdateAssignmentStatusForm(forms.Form):
    status = forms.ChoiceField(choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ])


class AttendanceForm(forms.Form):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        # Add other choices as needed
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, label='Attendance Status')
