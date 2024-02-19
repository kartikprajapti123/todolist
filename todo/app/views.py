from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter

# Create your views here.
from app.serializers import (
    #authentication
    UserSerializer,
    LoginSerializer,
    SignupSerializer,
    SendEmailSerilizer,
    ChangePasswordSerializer,
    #project
    ProjectSerializer,
    EmployeeSeralizer,
    TaskSerializer,
    TaskAssignmentSerializer,
    )
from app.custom_pagination import MyPagination
from django.contrib.auth import authenticate,login,logout
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import User,Token,Project,EmployeeProject,Task


from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserView(ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    
    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            user=User.objects.all()
            serializer=self.serializer_class(user,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"msg":"superuser only"},status=status.HTTP_400_BAD_REQUEST)
    
    def create(self,request):
        seriaizer=SignupSerializer(data=request.data)
        
        if seriaizer.is_valid(raise_exception=True):
            user=seriaizer.save()
            token=get_tokens_for_user(user)
            
            return Response({'token':token,"msg":"Signup Done Successfully"},status=status.HTTP_201_CREATED)
        
        return Response(seriaizer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False,methods=['post'],permission_classes=[AllowAny],authentication_classes=[JWTAuthentication])
    def login(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email=serializer.validated_data['email']
            password=serializer.validated_data['password']
            print(email,password)
            user=authenticate(email=email,password=password)
            print(user)
            if user is not None:
                print(user)
                login(request,user)
                token=get_tokens_for_user(user)
                return Response({'token':token,'msg':"Login done Succesfully"},status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'msg':"Invalid Email or Password"},status=status.HTTP_404_NOT_FOUND)
            
    
    @action(detail=False,methods=['post'],permission_classes=[AllowAny])
    def sendmail(self,request):
        serializer=SendEmailSerilizer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            email=serializer.validated_data['email']
            return Response({'msg':f"Email send successfully To {email} "},status=status.HTTP_202_ACCEPTED)
        
    @action(detail=False,methods=['post','get'],permission_classes=[AllowAny])
    def changepassword(self,request,*args, **kwargs):
        token=request.GET.get('token')
        if request.method=='GET':
            if not Token.objects.filter(token=token).exists():
                return Response({'msg':"Token is inavlid"},status=status.HTTP_205_RESET_CONTENT)
            
            return Response({'msg':"success token"},status=status.HTTP_201_CREATED)
        
        if request.method=="POST":
            user=Token.objects.filter(token=token)[0].user
            main_user=User.objects.get(email=user.email)
            serializer=ChangePasswordSerializer(data=request.data,context={'user':main_user})
            serializer.is_valid(raise_exception=True)
            
            return Response({'msg':f"Password Change Successfully of {main_user.email}"},status=status.HTTP_202_ACCEPTED)
            
            # serializer=ChangePasswordSerializer(data=request.data)
                
            
class ProjectView(ModelViewSet):
    queryset=Project.objects.all()
    serializer_class=ProjectSerializer
    pagination_class=MyPagination
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    search_fields=['project_name','description']
    filterset_fields=['project_name','description']
    
    ordering_fields=['created_at']
    
    
    # def get_permissions(self):
    #     if self.action in ['create', 'update', 'destroy']:
    #         return [IsAdminUser()]
    #     return super().get_permissions()
    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            
            serializer=self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'msg':"Project succesfully added"},status=status.HTTP_202_ACCEPTED)
            
        return Response({'msg':"You are not allowed to add Project"},status=status.HTTP_400_BAD_REQUEST)
            
            
    def update(self, request, *args, **kwargs):
        instance=self.get_object()
        print(instance)
        if request.user.is_superuser:
            
            serializer=self.serializer_class(instance=instance ,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'msg':"Update Successfully"},status=status.HTTP_202_ACCEPTED)
            
        return Response({'msg':"You are not allowed to Update Project"},status=status.HTTP_400_BAD_REQUEST)
    
    
    def destroy(self, request, *args, **kwargs):
        instance=self.get_object()
        if request.user.is_superuser:
            
            instance.delete()
            return Response({'msg':"Project succesfully Deleted"},status=status.HTTP_202_ACCEPTED)
            
        return Response({'msg':"You are not allowed to Delete Project"},status=status.HTTP_400_BAD_REQUEST)
                    
                    
    
class EmployeeView(ModelViewSet):
    serializer_class=EmployeeSeralizer
    
    def get_queryset(self):
        print(self.kwargs)
        return EmployeeProject.objects.filter(project_id=self.kwargs['project_pk'])
    
    # def get_permissions(self):
    #     if self.action in ['create', 'update', 'destroy']:
    #         return [IsAdminUser()]
    #     return super().get_permissions()

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            serializer=EmployeeSeralizer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'msg':"Employee in project is add Successfully"},status=status.HTTP_202_ACCEPTED)
        
        return Response({'msg':"You are not allow to do Add Employee"},status=status.HTTP_400_BAD_REQUEST)            
          
    def update(self, request, *args, **kwargs):
        instance=self.get_object()
        print(instance)
        if request.user.is_superuser:
            serializer=EmployeeSeralizer(instance=instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'msg':"Employee in project is Updated Successfully"},status=status.HTTP_202_ACCEPTED)
        
        return Response({'msg':"You are not allow to do Update in Employee"},status=status.HTTP_400_BAD_REQUEST)            
          
    def destroy(self, request, *args, **kwargs):
        print("hello")
        instance=self.get_object()
        print(instance)
        if request.user.is_superuser:
            instance.delete()
            return Response({'msg':"Employee in project is Deleted Successfully"},status=status.HTTP_202_ACCEPTED)
            
        return Response({'msg':"You are not allow to do Delete in Employee"},status=status.HTTP_404_NOT_FOUND)            
          
            
class TaskView(ModelViewSet):
    serializer_class=TaskSerializer
    permission_classes=[AllowAny]
    
    def get_queryset(self):
        return Task.objects.filter(project_id=self.kwargs['project_pk'])
    
    # def get_permissions(self):
    #     print(self.request)
    #     if self.action in ['create', 'update', 'destroy']:
    #         print(self.action)
    #         return [IsAdminUser()]
    #     return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            serializer=TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'msg':'Task created Successfully'},status=status.HTTP_202_ACCEPTED)
        
        return Response({'msg':"You are not allowed to create task"},status=status.HTTP_404_NOT_FOUND)      
        
    def update(self, request, *args, **kwargs):
        instance=self.get_object()
        if request.user.is_superuser:
            serializer=TaskSerializer(instance=instance ,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'msg':'Task Updated Successfully'},status=status.HTTP_202_ACCEPTED)
        
        return Response({'msg':"You are not allowed to update task"},status=status.HTTP_404_NOT_FOUND) 
    
    def destroy(self, request, *args, **kwargs):
        instance=self.get_object()
        if request.user.is_superuser:
            instance.delete()
            return Response({'msg':'Task Deleted Successfully'},status=status.HTTP_202_ACCEPTED)
        
        return Response({'msg':"You are not allowed to Delete task"},status=status.HTTP_404_NOT_FOUND) 
        
    
class TaskAssignmentView(ModelViewSet):

    serializer_class=TaskAssignmentSerializer
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    search_fields=['name','description']
    filterset_fields=['name','description']
    
    ordering_fields=['assigned_date']
    
    def get_queryset(self):
        print(self.kwargs)
        print(Task.objects.filter(employee_id=self.kwargs['employee_id']))
        return Task.objects.filter(employee_id=self.kwargs['employee_id'])
    
    # def get_permissions(self):
    #     print(self.request)
    #     if self.action in ['create', 'update', 'destroy']:
    #         print(self.action)
    #         return [IsAdminUser()]
    #     return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            serializer=TaskAssignmentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print(serializer.data)
            
            return Response({'msg':'Task created Successfully and mail send to employee'},status=status.HTTP_202_ACCEPTED)
        
        return Response({'msg':"You are not allowed to create task"},status=status.HTTP_404_NOT_FOUND)      
        
    def update(self, request, *args, **kwargs):
        instance=self.get_object()
        if request.user.is_staff:
            serializer=TaskAssignmentSerializer(instance=instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.update(instance, serializer.validated_data) 
            return Response({'msg':'Task Updated Successfully and mail send to employee'},status=status.HTTP_202_ACCEPTED)
            
        return Response({'msg':"You are not allowed to update task"},status=status.HTTP_404_NOT_FOUND) 
    
    def destroy(self, request, *args, **kwargs):
        instance=self.get_object()
        if request.user.is_superuser:
            instance.delete()
            return Response({'msg':'Task Deleted Successfully'},status=status.HTTP_202_ACCEPTED)
        
        return Response({'msg':"You are not allowed to Delete task"},status=status.HTTP_404_NOT_FOUND) 
        

    

        
