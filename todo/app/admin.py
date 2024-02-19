from django.contrib import admin

# Register your models here.
from .models import User,Token,Project,EmployeeProject,Task

admin.site.register(User)
admin.site.register(Token)
admin.site.register(Project)
admin.site.register(EmployeeProject)
admin.site.register(Task)


