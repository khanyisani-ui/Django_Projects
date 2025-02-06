from django.shortcuts import render, redirect, get_object_or_404
from apscheduler.schedulers.background import BackgroundScheduler
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Employee, Assignment, Attendance, Progress
from .forms import AssignmentForm, EmployeeForm, ProgressUpdateForm, AttendanceForm, UpdateAssignmentStatusForm
from functools import wraps
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.db.models import Q  # Import Q for complex lookups


# Decorator for manager-only views
def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.employee.role != 'manager':
            messages.error(request, "You do not have permission to access this page.") #Using messages framework
            return redirect('employee_dashboard' if request.user.is_authenticated else 'login') # Redirect to appropriate page
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# Index
def index(request):
    return render(request, 'tasks/index.html')

# Login Views
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('manager_dashboard' if user.employee.role == 'manager' else 'employee_dashboard')
        else:
            messages.error(request, "Invalid username or password") # Using messages framework
            return render(request, 'tasks/login.html')
    return render(request, 'tasks/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Manager Views

@login_required
@manager_required
def manager_dashboard(request):
    assignments = Assignment.objects.all()
    employees = Employee.objects.all()
    context = {
        'assignments': assignments,
        'employees': employees,
    }
    return render(request, 'tasks/manager_dashboard.html', context)

@login_required
@manager_required
def create_assignment(request):
    if request.method == 'POST':
        assignment_form = AssignmentForm(request.POST)

        if assignment_form.is_valid():
            assignment = assignment_form.save()  # Save the assignment

            messages.success(request, "Assignment created successfully!")
            return redirect('employee_dashboard')  # Redirect immediately after creating assignment
        else:
            messages.error(request, "There was an error creating the assignment. Please correct the form.")
    else:
        assignment_form = AssignmentForm()

    context = {'assignment_form': assignment_form}  # Only pass the assignment form
    return render(request, 'tasks/create_assignment.html', context)

@login_required
@manager_required
def update_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully!")
            return redirect('manager_dashboard')
        else:
            messages.error(request, "Error updating assignment. Please correct the form below.")
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'tasks/assignment_form.html', {'form': form, 'form_type': 'update'})

@login_required
@manager_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment.delete()
    messages.success(request, "Assignment deleted successfully!")
    return redirect('manager_dashboard')

@login_required
@manager_required
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the User form
            employee = Employee.objects.create(user=user, role=form.cleaned_data['role']) # Create the Employee
            messages.success(request, "Employee created successfully!")
            return redirect('manager_dashboard')
        else:
            messages.error(request, "Error creating employee. Please correct the form below.")
    else:
        form = EmployeeForm()
    return render(request, 'tasks/employee_form.html', {'form': form, 'form_type': 'create'})

@login_required
@manager_required
def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee.user) # Pass the User instance
        if form.is_valid():
            user = form.save()  # Save the User form
            employee.role = form.cleaned_data['role'] # Update the employee role
            employee.save()
            messages.success(request, "Employee updated successfully!")
            return redirect('manager_dashboard')
        else:
            messages.error(request, "Error updating employee. Please correct the form below.")
    else:
        form = EmployeeForm(instance=employee.user, initial={'role': employee.role}) # Pre-populate role
    return render(request, 'tasks/employee_form.html', {'form': form, 'form_type': 'update'})

@login_required
@manager_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    employee.user.delete() # Delete the associated User, which will cascade to Employee
    messages.success(request, "Employee deleted successfully!")
    return redirect('manager_dashboard')

@login_required
@manager_required
def employee_details(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    attendances = Attendance.objects.filter(employee=employee)
    progresses = Progress.objects.filter(assignment__employee=employee)

    

    context = {
        'employee': employee,
        'attendances': attendances,
        'progresses': progresses,
        
    }
    return render(request, 'tasks/employee_details.html', context)


# Employee Views

@login_required
def employee_dashboard(request):
    """View for employee dashboard."""
    today = timezone.now().date()
    attendance = Attendance.objects.filter(employee=request.user.employee, date=today).first()

    if request.method == 'POST':
        if 'mark_attendance' in request.POST:
            if not attendance:
                Attendance.objects.create(employee=request.user.employee, status='present', date=today)
                messages.success(request, "Attendance marked successfully!")  # ✅ Show message
            return redirect('employee_dashboard')  # ✅ Redirect prevents reshowing message on refresh

    # Fetch assignments & latest progress
    assignments = Assignment.objects.filter(employee=request.user.employee)
    
    assignment_progress = []
    for assignment in assignments:
        latest_progress = Progress.objects.filter(assignment=assignment).order_by('-date').first()
        assignment_progress.append({
            'assignment': assignment,
            'latest_progress': latest_progress.percentage if latest_progress else 0,
        })

    context = {
        'attendance': attendance,
        'assignment_progress': assignment_progress,
    }
    return render(request, 'tasks/employee_dashboard.html', context)


@login_required
def update_assignment_status(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if assignment.employee != request.user.employee:
        messages.error(request, "You do not have permission to update this assignment.")
        return redirect('employee_dashboard')

    if request.method == 'POST':
        form = UpdateAssignmentStatusForm(request.POST)
        if form.is_valid():
            assignment.status = form.cleaned_data['status']
            assignment.save()
            messages.success(request, "Assignment status updated successfully!")
            return redirect('employee_dashboard')
        else:
            messages.error(request, "Error updating assignment status.")
    else:
        form = UpdateAssignmentStatusForm(initial={'status': assignment.status})
    return render(request, 'tasks/update_assignment_status.html', {'form': form, 'assignment': assignment})



@login_required
def view_attendance(request):
    """View for attendance - Employee sees own, Manager sees all."""
    today = timezone.now().date()
    is_manager = request.user.employee.role == 'manager'  # Determine role upfront
    marked_today = False  # Initialize marked_today to False

    if is_manager:  # Manager's view
        attendances = Attendance.objects.order_by('-date')
    else:  # Employee's view
        attendance = Attendance.objects.filter(employee=request.user.employee, date=today).first()
        attendances = Attendance.objects.filter(employee=request.user.employee).order_by('-date')

        if attendance:  # Check if attendance record exists
            marked_today = attendance.status == 'present' # Check if marked present

        if request.method == 'POST':
            if 'mark_attendance' in request.POST and not marked_today:
                if attendance: # Update existing attendance record
                    attendance.status = 'present'
                    attendance.save()
                else: # Create new attendance record
                   Attendance.objects.create(employee=request.user.employee, status='present', date=today)
                return redirect('attendance')  # Refresh page

    context = {
        'attendances': attendances,
        'is_manager': is_manager,
        'marked_today': marked_today,
    }
    return render(request, 'tasks/view_attendance.html', context)



@login_required
def mark_attendance(request):
    today = date.today()
    employee = request.user.employee

    attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)

    if not created:  # If the record exists already
        messages.info(request, "Your attendance for today has already been recorded.")
        return redirect('employee_dashboard')  # Redirect directly to the dashboard

    if request.method == 'POST':
        form = AttendanceForm(request.POST)  # If you're using a form
        if form.is_valid():
            attendance.status = form.cleaned_data['status']  # Assuming 'status' is in your form
            attendance.save()
            messages.success(request, "Attendance marked successfully!")
            return redirect('employee_dashboard') # Redirect after marking
    else:
        form = AttendanceForm() # If you are using a form

    return render(request, 'tasks/mark_attendance.html', {'form': form})

@login_required
def attendance_report(request):
    if request.user.is_staff:
        attendances = Attendance.objects.all()
    else:
        employee = request.user.employee
        attendances = Attendance.objects.filter(employee=employee)
    return render(request, 'tasks/attendance_report.html', {'attendances': attendances})

@login_required
def view_progress(request):
    if request.user.is_staff:
        progress_records = Progress.objects.all()
    else:
        employee = request.user.employee
        progress_records = Progress.objects.filter(assignment__employee=employee)

    context = {'progress_records': progress_records}
    return render(request, 'tasks/view_progress.html', context)


@login_required
def update_progress(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)

    # Correct Permission Check:
    if request.user.is_staff or assignment.employee.user == request.user:
        try:
            progress = Progress.objects.filter(assignment=assignment).latest('date')
        except Progress.DoesNotExist:
            progress = Progress(assignment=assignment)
            progress.save()

        if request.method == 'POST':
            form = ProgressUpdateForm(request.POST, instance=progress)
            if form.is_valid():
                form.save()
                messages.success(request, "Progress updated successfully!")
                return redirect('employee_dashboard' if not request.user.is_staff else 'manager_dashboard')
            else:
                messages.error(request, "There was an error updating the progress. Please correct the form.")
        else:
            form = ProgressUpdateForm(instance=progress)

        context = {'form': form, 'assignment': assignment}
        return render(request, 'tasks/update_progress.html', context)
    else:
        messages.error(request, "You don't have permission to update this assignment's progress.")
        return redirect('employee_dashboard' if not request.user.is_staff else 'manager_dashboard')

def mark_absent_task():
    today = date.today()

    #Efficiently get users who haven't marked attendance today.
    absent_employees = User.objects.filter(
        Q(employee__role='employee'), # Only consider regular employees
        ~Q(attendance__date=today) # Exclude users with attendance records today
    )

    for employee in absent_employees:
        Attendance.objects.create(employee=employee, date=today, status='absent') # Create absent record

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(mark_absent_task, 'cron', hour=0, minute=0)  # Run daily at midnight
    scheduler.start()