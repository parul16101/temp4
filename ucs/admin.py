"""
Django admin for project ucs

This module is for registering the classes in models.py
"""


from django.contrib import admin

# Register your models here.

from .models import Question, User, Category, Assignment, Assessment, Group,  Assigned_group, Assigned_question, Group_member, Dataset


# Register your models here.
admin.site.register(Question)
admin.site.register(User)
admin.site.register(Category)

admin.site.register(Assignment)

admin.site.register(Assessment)
admin.site.register(Group)
admin.site.register(Assigned_question)
admin.site.register(Assigned_group)
admin.site.register(Group_member)
admin.site.register(Dataset)
