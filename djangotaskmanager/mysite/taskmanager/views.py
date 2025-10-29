# from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q # Если нужны будут обращения к разным моделям использовать Q

from .models import Project, ProjectMember, Task
from .forms import ProjectChangeOwnerForm

"""
Регистрация
Дашборд
Проекты
Задачи
Комментарии
"""


class RegisterView(CreateView):
    """Представление для регистрации пользователя

    **model**: Модель с которой работает форма

    **form_class**: Стандартная или не стандартная форма для заполнения данными

    **template_name**: Путь к html-шаблону

    **success_url**: Перенаправление на URL после успешного заполнения формы

    """

    model = User
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        # Используем встроенную форму логина
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Добро пожаловать, {self.object.username}!")
        return response


class DashboardView(LoginRequiredMixin, ListView):
    """
    Представление для отображение задач и проектов пользовтеля
    """

    template_name = "taskmanager/dashboard.html"
    context_object_name = "user_projects"
    login_url = "login"  # Указываем куда перенаправлять если не аутентифицирован

    def get_queryset(self):
        return Project.objects.filter(members__user=self.request.user).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_tasks"] = Task.objects.filter(assignees__user=self.request.user)
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Представления для создание проекта"""

    model = Project
    fields = ["name", "description"]
    template_name = "taskmanager/project_form.html"

    def get_success_url(self):
        return reverse_lazy("project_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        # Создаем проект, участника, а потом назначаем владельцем
        project = form.save(commit=False)
        project.save()

        ProjectMember.objects.create(
            project=project, user=self.request.user, role="owner"
        )
        return super().form_valid(form)


class ProjectListView(LoginRequiredMixin, ListView):
    """Представления для отображения списка проектов"""

    model = Project
    template_name = "taskmanager/project_list.html"
    login_url = "login"

    def get_queryset(self):
        return Project.objects.filter(members__user=self.request.user).distinct()


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Представление для просмотра проекта"""

    model = Project
    template_name = "taskmanager/project_detail.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования проекта"""

    model = Project
    fields = ["name", "description"]
    template_name = "taskmanager/project_update_form.html"

    def get_success_url(self):
        return reverse_lazy("project_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        if not self._user_is_project_owner(project):
            messages.error(self.request, "Only owner can edit this project")
            return context

        form = ProjectChangeOwnerForm()

        current_owner = project.get_owner()
        members = project.members.exclude(user=current_owner)

        choices = []
        choices.append(("", "Do not change"))
        for member in members:
            display_text = str(member)
            choices.append((member.id, display_text))

        form.fields["new_owner"].choices = choices

        context["current_owner"] = current_owner
        context["members"] = members
        context["owner_form"] = form

        return context

    def _user_is_project_owner(self, project):
        return project.members.filter(user=self.request.user, role="owner").exists()

    def form_valid(self, form):
        project = form.save()

        new_owner_id = self.request.POST.get("new_owner")
        if new_owner_id:
            self._transfer_ownership(project, new_owner_id)

        messages.success(self.request, "Project updated")
        return super().form_valid(form)

    def _transfer_ownership(self, project, new_owner_id):
        try:
            new_owner_member = ProjectMember.objects.get(
                id=new_owner_id, project=project
            )
            current_owner_member = project.members.get(role="owner")

            if new_owner_member == current_owner_member:
                messages.warning(self.request, "User is already the owner")
                return

            # Смена ролей
            current_owner_member.role = "admin"
            current_owner_member.save()
            new_owner_member.role = "owner"
            new_owner_member.save()

            messages.success(
                self.request, f"Ownership is given to {new_owner_member.user.username}"
            )
        except ProjectMember.DoesNotExist:
            messages.error(self.request, "Project member does not exist")


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Представления для создания задачи"""

    model = Task
    fields = ["title", "description", "priority", "due_date"]
    template_name = "taskmanager/task_form.html"

    def get_success_url(self):
        return reverse_lazy("task_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.creator = self.request.user
        
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        form.instance.project = project

        return super().form_valid(form)
    
class TaskListView(LoginRequiredMixin, ListView):
    """Представление для отображения списка задач"""
    model = Task
    template_name = "taskmanager/task_list.html"
    login_url = "login"
    
    def get_queryset(self):
        return Task.objects.filter(
            Q(creator=self.request.user) | Q(assignees__user = self.request.user)
        ).distinct()


class TaskDetailView(LoginRequiredMixin,DetailView):
    """Представления для отображения задачи"""
    model = Task
    template_name = "taskmanager/task_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context[""] = 
        return context

class TaskUpdateView(LoginRequiredMixin,UpdateView):
    """Представления для редактирования задачи"""
    model = Task
    fields = ["title", "description", "priority", "due_date"]
    # TODO Доделать и отрефакторить 
