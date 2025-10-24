from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView,
)
from .models import Project, ProjectMember, Task
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

"""
Регистрация
Проекты
Задачи
Комментарии
"""


class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Добро пожаловать, {self.object.username}!")
        return response


class DashboardView(LoginRequiredMixin, ListView):
    template_name = "taskmanager/dashboard.html"
    context_object_name = "user_projects"
    login_url = "login"  # Указываем куда перенаправлять если не аутентифицирован

    def get_queryset(self):
        #Q objects для ИЛИ 
        return Project.objects.filter(
            Q(owner=self.request.user) | Q(members__user=self.request.user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_tasks"] = Task.objects.filter(assignees__user=self.request.user)
        return context


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "taskmanager/project_list.html"
    login_url = "login"

    def get_queryset(self):
        return Project.objects.filter(
            Q(owner=self.request.user) | Q(members__user=self.request.user)
        ).distinct()


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ["name", "description"]
    template_name = "taskmanager/project_form.html"
    def get_success_url(self):
        return reverse_lazy('project_list')
    
    def form_valid(self,form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "taskmanager/project_detail.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    
class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = ["name", "description", "owner"]
    template_name = "taskmanager/project_update_form.html"
    def get_success_url(self):
        return reverse_lazy('project_detail')
    def form_valid(self,form):
        
        pass
        