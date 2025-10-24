from django.contrib import admin
from .models import (
    Project,
    ProjectMember,
    Status,
    Task,
    Assignee,
    Comment,
    Attachment,
    Activity,
    ProjectLabel,
    TaskLabel,
)

# Register your models here.

admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(Status)
admin.site.register(Task)
admin.site.register(Assignee)
admin.site.register(Comment)
admin.site.register(Attachment)
admin.site.register(Activity)
admin.site.register(ProjectLabel)
admin.site.register(TaskLabel)