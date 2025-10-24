from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.utils import timezone

# Create your models here.


class Project(models.Model):
    name = models.CharField(
        max_length=100,
    )
    description = models.TextField()
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Project Owner",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name

    def clean(self):
        """Валидация"""
        if len(self.name.strip()) < 2:
            raise ValidationError(
                {"name": "Projects name must be at least 2 characters long"}
            )


class ProjectMember(models.Model):
    ROLES = [
        ("admin", "Administrator"),
        ("member", "Member"),
        ("viewer", "Viewer"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["project", "user"]
        verbose_name = "Project member"
        verbose_name_plural = "Project members"

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"

    def clean(self):
        """Владелец не как участник"""
        if self.user == self.project.owner:
            raise ValidationError(
                "Project ownwer is automatically a member and cannot be added"
            )


class Status(models.Model):
    name = models.CharField(max_length=50, verbose_name="Status Name")
    order = models.IntegerField(verbose_name="Display Order")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="statuses"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        unique_together = ["project", "order"]
        verbose_name = "Status"
        verbose_name_plural = "Statuses"

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_order = models.IntegerField(default=0)
    PRIORITIES = [
        ("1", "Highest"),
        ("2", "High"),
        ("3", "Medium"),
        ("4", "Low"),
        ("5", "Lowest"),
        ("6", "Not a Priority"),
    ]
    priority = models.CharField(
        max_length=1, choices=PRIORITIES, default="3", verbose_name="Priority Level"
    )
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Due Date")
    estimated_hours = models.DurationField(
        null=True, blank=True, verbose_name="Estimated Hours"
    )
    actual_hours = models.DurationField(
        null=True, blank=True, verbose_name="Actual Time Spent"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
        verbose_name="Task Creator",
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tasks",
        verbose_name="Task Status",
    )

    class Meta:
        ordering = ["task_order", "-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title

    def clean(self):
        """Валидация дат и времени"""
        if self.due_date and self.due_date < timezone.now():
            raise ValidationError({"due_date": "Due date cannot be in the past"})


class Assignee(models.Model):
    ROLES = [
        ("assignee", "Assignee"),
        ("reviewer", "Reviewer"),
        ("watcher", "Watcher"),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="assignees")
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="task_assignments"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Time of assignation"
    )
    role = models.CharField(max_length=20, choices=ROLES, default="assignee")

    class Meta:
        unique_together = [
            "task",
            "user",
        ]  # Один пользовтаель на задачу может назначен только один раз
        verbose_name = "Assignee"
        verbose_name_plural = "Assignees"

    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.role})"


class Comment(models.Model):
    content = models.TextField(verbose_name="Comment Content")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to="task_attachments/%Y/%m/%d/", verbose_name="Attached File"
    )
    name = models.CharField(max_length=255, blank=True, verbose_name="File Name")

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    def __str__(self):
        return self.name if self.name else f"Attachment {self.id}"


class Activity(models.Model):
    ACTIONS = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
        ("status_changed", "Status Changed"),
        ("assigned", "Assigned"),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="activities")
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="activities"
    )
    action_type = models.CharField(max_length=50, choices=ACTIONS)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    def __str__(self):
        return f"{self.user.username} {self.action_type} task {self.task.id}"


class ProjectLabel(models.Model):
    name = models.CharField(max_length=50, verbose_name="Label Name")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="labels"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    color = models.CharField(
        max_length=7, default="#808080", verbose_name="Label Color"
    )

    class Meta:
        unique_together = ["project", "name"]
        verbose_name = "Project Label"
        verbose_name_plural = "Project Labels"

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class TaskLabel(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task_labels")
    label = models.ForeignKey(
        ProjectLabel, on_delete=models.CASCADE, related_name="task_labels"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["task", "label"]
        verbose_name = "Task Label"
        verbose_name_plural = "Task Labels"

    def __str__(self):
        return f"{self.task.title} - {self.label.name}"
