
from django.contrib import admin
from django.urls import path,include
from app import views
from rest_framework_nested.routers import DefaultRouter,NestedDefaultRouter

router=DefaultRouter()

router.register('user',views.UserView,basename="user")
router.register('project',views.ProjectView,basename="project")

nested_router=NestedDefaultRouter(router,'project',lookup='project')
nested_router.register('employee',views.EmployeeView,basename="project-employee")
nested_router.register('task',views.TaskView,basename="project-task")

newRouter=DefaultRouter()
newRouter.register('task',views.TaskAssignmentView,basename='project-employee-task')


urlpatterns = [
    path('',include(router.urls)),
    path('',include(nested_router.urls)),
    path('project/<int:project_id>/employee/<int:employee_id>/',include(newRouter.urls)),
    
    
    
]
