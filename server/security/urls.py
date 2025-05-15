from django.urls import path
from .views import StudentCreationEndpoint, EmployeeCreationEndpoint, Login, StudentList, EmployeeList, EmployeeEdit, EmployeeGetById, StudentGetById, StudentEdit, EmployeeTeacherList, ChangePassword # Importez votre vue


urlpatterns = [ 
    path('login/', Login.as_view(), name='login'),
    path('create-student/', StudentCreationEndpoint.as_view(), name='create-student'),
    path('student/list/', StudentList.as_view(), name='list-student'),
    path('student/<int:id>/', StudentGetById.as_view(), name='get-student'),
    path('student/edit/<int:student_id>/', StudentEdit.as_view(), name='edit-student'),
    path('create-employee/', EmployeeCreationEndpoint.as_view(), name='create-employee'),
    path('employee/list/', EmployeeList.as_view(), name='list-employee'),
    path('employee/edit/<int:employee_id>/', EmployeeEdit.as_view(), name='edit-employee'),
    path('employee/<int:employee_id>/', EmployeeGetById.as_view(), name='get-employee'),
    path('employee/teacher/list/', EmployeeTeacherList.as_view(), name='list-employee-teacher'),
    path('change-password/', ChangePassword.as_view(), name='change-password'),
]

