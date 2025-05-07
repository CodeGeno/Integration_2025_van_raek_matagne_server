from django.urls import path
from .views import StudentCreationEndpoint, EmployeeCreationEndpoint, Login, StudentList, EmployeeList, EmployeeEdit, EmployeeGet, StudentGetById # Importez votre vue


urlpatterns = [
   
    path('login/', Login.as_view(), name='login'),
    path('create-student/', StudentCreationEndpoint.as_view(), name='create-student'),
    path('student/list/', StudentList, name='list-student'),
    path('student/<int:id>/', StudentGetById, name='get-student'),
    path('student/edit/<int:student_id>/', StudentEdit, name='edit-student'),
    path('create-employee/', EmployeeCreationEndpoint.as_view(), name='create-employee'),
    path('employee/list/', EmployeeList, name='list-employee'),
    path('employee/edit/<int:employee_id>/', EmployeeEdit, name='edit-employee'),
    path('employee/<int:employee_id>/', EmployeeGet, name='get-employee'),
   
]
