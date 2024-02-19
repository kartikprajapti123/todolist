from rest_framework import serializers 
import uuid
import re
from .models import User,Token,Project,EmployeeProject,Task
import threading
from django.core.mail import send_mail,EmailMessage

def sendmail(email,token):
    
        subject="Checking the email send"
        message=f"Hello yout change password link is \n http://127.0.0.1:8000/user/changepassword/?token={token}"  
        from1="kartikprajapati26122004@gmail.com"
        to=[email,]      
        send_mail(subject,message,from1,to)
        
def SendMailWhenAsssign(email,task):
        subject="Task Assigned"
        message=f"You are assigned task\nTask is {task.project_name}\ndescription={task.description}\nDeadline={task.deadline}\n This task assigned by Admin User \nGood luck for the task \nGive your best"
        from1="kartikprajapati26122004@gmail.com"
        to=[email,]      
        send_mail(subject,message,from1,to)

class UserSerializer(serializers.ModelSerializer):
    email=serializers.EmailField()
    class Meta:
        model=User
        fields=['id','email']
        
    def update(self,instance,validated_data):
        instance.email=validated_data.get('email',instance.email)
        
        instance.save()
        
        return instance
    
        
        
class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField()
    class Meta:
        model=User
        fields=['id','email','password']
       
class SignupSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(write_only=True)
    
    
    class Meta:
        model=User
        fields=['id','email','password','password2']
         
        
    def validate(self, attrs):
        email=attrs.get('email')
        password=attrs.get('password')
        password2=attrs.get('password2')
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}$'
        print(re.match(email,email_pattern))
        emailCheck=User.objects.filter(email=email)
        if emailCheck.exists():
            raise serializers.ValidationError("Email Already exists")
            
        elif not re.match(email_pattern,email):
            raise serializers.ValidationError("Inavlid Email")
        
        elif len(password)<8 or len(password2) >14:
            raise serializers.ValidationError("password Length should be between 8 to 14")
        
        elif password!=password2:
            raise serializers.ValidationError("Password are not matching")
        
        
        
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')  # Remove password from validated data
        # Remove password from validated data
        user = User.objects.create(**validated_data)
        user.set_password(password)  # Hash the password before saving
        user.save()
        
        return user
        
        
class SendEmailSerilizer(serializers.ModelSerializer):
    email=serializers.EmailField()
    
    class Meta:
        model=User
        fields=['email']
        
    def validate(self, attrs):
        email=attrs.get('email')
        checkUser=User.objects.filter(email=email)
        if not checkUser.exists():
            raise serializers.ValidationError("This is not Logged before try another")
        
        
        token=uuid.uuid4()
        Token.objects.create(token=token,user=checkUser[0])
        
        sending=threading.Thread(target=sendmail,args=(f'{email}',f'{token}'))
        sending.start()
        return attrs
    
    
    
        
class ChangePasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=14)
    password2=serializers.CharField(max_length=14)
        
    def validate(self, attrs):
        password=attrs.get('password')
        password2=attrs.get('password2') 
        
        user=self.context.get('user')
        
        if len(password)<8 or len(password) >14 :
            raise serializers.ValidationError('Password length should e between 8 to 14')
        
        elif password2 != password:
            raise serializers.ValidationError("Password are not matching") 
        
        user.set_password(password)
        user.save()    
            
        
        return attrs
    
class ProjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Project
        fields=['id','project_name','description','start_date','end_date','created_at']
        
        
    def update(self, instance, validated_data):
        instance.project_name=validated_data.get('project_name',instance.project_name)
        instance.description=validated_data.get('description',instance.description)
        instance.start_date=validated_data.get('start_date',instance.start_date)
        instance.end_date=validated_data.get('end_date',instance.end_date)
        instance.created_at=validated_data.get('created_at',instance.created_at)
        
        instance.save()
        return instance
        
class EmployeeSeralizer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    project=ProjectSerializer(read_only=True)
    
    class Meta:
        model=EmployeeProject
        fields=['id','user','project','role']
        
        
    def update(self, instance, validated_data):
        
        instance.role=validated_data.get('role',instance.role)
        instance.save()        
        return instance
    
class TaskSerializer(serializers.ModelSerializer):
    project=ProjectSerializer(read_only=True)

    class Meta:
        model=Task
        fields=['id','name','description','deadline','project','status','created_at']
        
    def update(self, instance, validated_data):
        print(validated_data)
        instance.name=validated_data.get('name',instance.name)
        instance.description=validated_data.get('description',instance.description)
        instance.status=validated_data.get('status',instance.status)
        instance.created_at=validated_data.get('created_at',instance.created_at)
        instance.save()
        
        return instance
    
class TaskAssignmentSerializer(serializers.ModelSerializer):
    employee=EmployeeSeralizer(read_only=True)
    
    class Meta:
        model=Task
        fields=['id','name','status','description','status','created_at','employee','assigned_date','completion_date']
        
    
    def save(self, **kwargs):
        ("Email are send")