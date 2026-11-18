from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from . models import Project
from .serializers import ProjectSerializer
from.models import AssignedProject,Task
from.serializers import AssignedProjectSerializer,TaskSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from planner.utils import generate_tasks
from django.db import transaction
from planner.pagenations import CustomPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.permissions import IsAdmin,IsCoordinator,IsDeveloper
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class ProjectListCreateView(ListCreateAPIView):
    pagination_class= CustomPagination

    queryset = Project.objects.filter(active_status =True)
    serializer_class = ProjectSerializer
    http_method_names = ['get','post']
    permission_classes = [JWTAuthentication]
    def get_permissions(self):
        permissions =  []
        if self.request.method in ['POST']:
            permissions = [IsAdmin]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]
    
class ProjectRetriveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    lookup_field= 'uuid'
    queryset = Project.objects.filter(active_status =True)
    serializer_class = ProjectSerializer
    http_method_names = ['get','patch','delete']
    permission_classes = [JWTAuthentication]
    def get_permissions(self):
        permissions =  []
        if self.request.method in ['PATCH','DELETE']:
            permissions = [IsAdmin]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]
    def perform_destroy(self, instance):
        instance.active_status = False
        instance.save()

class AssignedProjectListCreateView(ListCreateAPIView):
    pagination_class= CustomPagination
    queryset= AssignedProject.objects.filter(active_status =True).select_related('project','coordinator').prefetch_related('developers')
    serializer_class = AssignedProjectSerializer
    http_method_names = ['get','post']
    permission_classes = [JWTAuthentication]
    def get_permissions(self):
        permissions =  []
        if self.request.method in ['POST']:
            permissions = [IsAdmin]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

class AssignedProjectRetriveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    lookup_field= 'uuid'
    queryset= AssignedProject.objects.filter(active_status =True).select_related('project','coordinator').prefetch_related('developers')
    serializer_class = AssignedProjectSerializer
    http_method_names = ['get','patch','delete']
    permission_classes = [JWTAuthentication]
    def get_permissions(self):
        permissions =  []
        if self.request.method in ['PATCH','DELETE']:
            permissions = [IsAdmin]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

    def perform_destroy(self, instance):
        instance.active_status = False
        instance.save()

class TaskListCreateView(ListCreateAPIView):
    pagination_class= CustomPagination
    def get_queryset(self):
        uuid = self.request.query_params.get('project')
        if uuid:

             assigned_project = AssignedProject.objects.get(uuid=uuid)
             tasks = assigned_project.assigned_tasks.filter(active_status =True).select_related('assigned_project','assigned_to')
             return tasks
        return Task.objects.none()
    serializer_class = TaskSerializer
    http_method_names = ['get','post']
    permission_classes = [JWTAuthentication]
    def get_permissions(self):
        permissions =  []
        if self.request.method in ['POST']:
            permissions = [IsCoordinator]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

class TaskRetriveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    lookup_field= 'uuid'
    queryset= Task.objects.filter(active_status =True).select_related('assigned_project','assigned_to')
    serializer_class = TaskSerializer
    http_method_names = ['get','patch','delete']
    permission_classes = [JWTAuthentication]
    def get_permissions(self):
        permissions =  []
        if self.request.method in ['PATCH','DELETE']:
            permissions = [IsCoordinator]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

    def perform_destroy(self, instance):
        instance.active_status = False
        instance.save()

class TaskCreateWithAI(APIView):
    http_method_names = ['post']
    permission_classes = [JWTAuthentication]
    def get_permissions(self):
        permissions =  []
        if self.request.method in ['POST']:
            permissions = [IsCoordinator]
        return [permission() for permission in permissions]
    def post(self,request,*args,**kwargs):
        uuid= kwargs.get('uuid')
        try:
            assigned_project= AssignedProject.objects.get(uuid=uuid)
            result =generate_tasks(assigned_project)
            tasks = [Task(title =task.title,
                          description= task.description,
                          assigned_project=assigned_project,
                          assigned_to_id= task.developer_id,
                          priority=task.priority) for task in result.tasks]
            with transaction.atomic():
                Task.objects.bulk_create(tasks)
                data = {'msg':'Tasks assigned successfully'}
                return Response(data,status=200)
        except:
            data = {'msg':'Failed to create Tasks'}
            return Response(data,status=400)
    
        
