from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('employee_details/<int:employee_id>/', views.employee_details, name='employee_details'),
    path('create_employee/', views.create_employee, name='create_employee'),
    path('update_employee/<int:employee_id>/', views.update_employee, name='update_employee'),
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    
    # Assignment Paths
    path('create_assignment/', views.create_assignment, 
    name='create_assignment'),
    path('update_assignment/<int:assignment_id>/', views.update_assignment, name='update_assignment'),
    path('delete_assignment/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    
    # Attendance Paths
    path('attendance/', views.view_attendance, name='attendance'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance_report/', views.attendance_report, name='attendance_report'),
    
    

    # Progress Paths
    path('progress/', views.view_progress, name='progress'),
    path('update_progress/<int:assignment_id>/', views.update_progress, name='update_progress'),


    # Employee Paths
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('update_assignment_status/<int:assignment_id>/', views.update_assignment_status, name='update_assignment_status'),

    
]