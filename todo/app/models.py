from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.utils import timezone
import threading
from ckeditor.fields import RichTextField
# apps.py


from .manager import CustomUserManager


class User(AbstractUser):
    username = models.CharField(default="",max_length=20,null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class Token(models.Model):
    token=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="token_user")
    
    
class Project(models.Model):
    project_name = models.CharField(max_length=100)
    description = RichTextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status_choices=[
        ('TO DO','To Do'),
        ('IN PR0GRESS',"In Progress"),
        ('COMPLETED', 'Completed'),
        ]
    status = models.CharField(max_length=20, choices=status_choices, default='TODO')
    
    def __str__(self):
        return f"id={self.id},{self.project_name}"
    
class EmployeeProject(models.Model):
    
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True)
    
    
    def __str__(self):
        return f"id={self.id}/employee={self.user.email}/Project={self.project.project_name}"
    
class Task(models.Model):
    name = models.CharField(max_length=100)
    description = RichTextField()
    deadline = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status_choices=[
        ('TO DO','To Do'),
        ('IN PR0GRESS',"In Progress"),
        ('COMPLETED', 'Completed'),
        ]
    status = models.CharField(max_length=20, choices=status_choices, default='TODO')
    created_at=models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(EmployeeProject, on_delete=models.CASCADE,default=1)
    assigned_date = models.DateTimeField(default=timezone.now, editable=False)  # Set default value to current time
    completion_date = models.DateTimeField(null=True, blank=True)
    # employee = models.ForeignKey(EmployeeProject, on_delete=models.CASCADE,default="")
    # assigned_date = models.DateTimeField(auto_now_add=True)
    # completion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"id={self.id}/{self.name}"
    
@receiver(post_save, sender=Task)
def send_notify_mail(sender, instance, created, **kwargs):
    task=instance
    email=instance.employee.user.email
    print(task)
    if created:
        print("hello")
        def SendMailWhenAsssign(email,task):
            subject="Task Assigned"
            message=f"You are assigned task\nTask = {task.name}\ndescription = {task.description}\nDeadline = {task.deadline}\n This task assigned by Admin User \nGood luck for the task \nGive your best"
            from1="kartikprajapati26122004@gmail.com"
            to=[email,]      
            send_mail(subject,message,from1,to)

        # sending=threading.Thread(target=SendMailWhenAsssign,args=[f'{}'])

        notify=threading.Thread(target=SendMailWhenAsssign,args=(email,task))
        notify.start()
    