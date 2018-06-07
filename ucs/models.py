"""
Django models for ucs project.

This module contains several classes. Each class is represented as table in the database.
The member variables in class are considered as columns of table.
"""


from __future__ import unicode_literals
from django.db import models


class User(models.Model):
    ## @var username.
    # This is a class variable. Data type of this variable is "string". It is used to store username. Maximum length of string allowed to store in it is 200. 
    username = models.CharField(max_length=200)
    ## @var email.
    # This is a class variable. Data type of this variable is "string". It is used to store email-Id. Maximum length of string allowed to store in it is 200.
    email = models.CharField(max_length=200)
    ## @var password.
    # This is a class variable. Data type of this variable is "string". It is used to store password. Maximum length of string allowed to store in it is 200.
    password = models.CharField(max_length=200)
    ## @var admin_user.
    # This is a class variable. Data type of this variable is "boolean". It is used to identify if a user is admin. By default the user is NOT an admin.  
    admin_user = models.BooleanField(default=False)
    def __unicode__(self):
        return self.username

class Category(models.Model):
    ## @var category_text.
    # This is a class variable. Data type of this variable is "string". It is used to store category. By default it's value is "unknown". Maximum length of string allowed to store in it is 200.
    category_text = models.CharField(max_length=200, default="unknown")
    ## @var num_of_question.
    # This is a class variable. Data type of this variable is "integer". It is used to store count of questions. By default it's value is 0.
    num_of_question = models.IntegerField(default=0)
    def __unicode__(self):
        return self.category_text

class Question(models.Model):
    ## @var question_text.
    # This is a class variable. Data type of this variable is "string". It is used to store question_text. Maximum length of string allowed to store in it is 10000.
    question_text = models.CharField(max_length=10000, blank=True, null=True)
    ## @var unit.
    # This is a class variable. Data type of this variable is "string". It is used to store unit. Maximum length of string allowed to store in it is 200.
    unit = models.CharField(max_length=200, blank=True, null=True)
    ## @var close_date.
    # This is a class variable. Data type of this variable is "string". It is used to store close date. 
    close_date = models.CharField(max_length=200, blank=True, null=True)
    ## @var true_value.
    # This is a class variable. Data type of this variable is "string". It is used to store true value. Maximum length of string allowed to store in it is 200.
    true_value = models.CharField(max_length=200, blank=True, null=True)
    ## @var upload_date
    # This is a class variable. Data type of this variable is "string". It is used to store date when the question was uploaded. 
    upload_date = models.CharField(max_length=200, blank=True, null=True)
    ## @var uploader_id
    # This is Foreign key. It is a reference to a user.
    uploader_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ## @var category
    # This is Foreign key. It is a reference to a category.
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ## @var question_type.
    # This is a class variable. Data type of this variable is "boolean". It is used to identify type of question. By default it's value is True. 
    question_type = models.BooleanField(default=True)
    ## @var forecast
    # This is a class variable. Data type of this variable is "boolean". It is used to identify if it is a forecast. By default it's value is True.
    forecast = models.BooleanField(default=True)
    ## @var corporate_training
    # This is a class variable. Data type of this variable is "boolean". It is used to identify if it is a corporate training. By default it's value is True.
    corporate_training = models.BooleanField(default=True)
    ## @var allow_assessment
    # This is a class variable. Data type of this variable is "boolean". It is used to idetify if assessment is allowed. By default it's value is True.
    allow_assessment = models.BooleanField(default=True)
    ## @var num_of_choices
    # This is a class variable. Data type of this variable is "integer". It is used to store count of options for a specific question. By default it's value is 0.
    num_of_choices = models.IntegerField(default=0)
    ## @var question_source
    # This is a class variable. Data type of this variable is "string". It is used to store source of question. Maximum length of string allowed to store in it is 1000.
    question_source = models.CharField(max_length=1000, blank=True, null=True)
    ## @var question_description
    # This is a class variable. Data type of this variable is "string". It is used to store description of question. Maximum length of string allowed to store in it is 10000.
    question_description = models.CharField(max_length=10000, blank=True, null=True)
    def __unicode__(self):
        return self.question_text

class Assignment(models.Model):
    ## @var assignment_name
    # This is a class variable. Data type of this variable is "string". It is used to store name of an assignment. Maximum length of string allowed to store in it is 1000.
    assignment_name = models.CharField(max_length=1000, blank=True, null=True)
    ## @var due_date
    # This is a class variable. Data type of this variable is "string". It is used to store due date for the assignment.
    due_date = models.CharField(max_length = 200, blank=True, null=True)
    def __unicode__(self):
        return self.assignment_name

class Assessment(models.Model):
    ## @var question_id
    # This is Foreign key. It is a reference to a question.
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    ## @var user_id
    # This is Foreign key. It is a reference to a user.
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ## @var option_text
    # This is a class variable. Data type of this variable is "string". It is used to store text of option. Maximum length of string allowed to store in it is 50. 
    option_text = models.CharField(max_length=50, default="NA")
    ## @var answer_text
    # This is a class variable. Data type of this variable is "string". It is used to store text of answer. Maximum length of string allowed to store in it is 50. 
    answer_text = models.CharField(max_length=50, default="NA")
    ## @var operator
    # This is a class variable. Data type of this variable is "string". It is used to store operator. Maximum length of string allowed to store in it is 2.
    operator = models.CharField(max_length=2, default="LE")
    ## @var date_of_assessment
    # This is a class variable. Data type of this variable is "string". It is used to store date of assessment. Maximum length of string allowed to store in it is 50.
    date_of_assessment = models.CharField(max_length=50)
    ## @var time_of_assessment
    # This is a class variable. Data type of this variable is "string". It is used to store time of assessment. Maximum length of string allowed to store in it is 50.
    time_of_assessment = models.CharField(max_length=50)
    ## @var details_of_assessment
    # This is a class variable. Data type of this variable is "string". It is used to store details of assessment. Maximum length of string allowed to store in it is 1000.
    details_of_assessment = models.CharField(max_length=1000, blank=True, null=True)
    def __unicode__(self):
        return 'Object: '+self.question_id.question_text+'---'+self.option_text+'---'+self.user_id.username

class Group(models.Model):
    ## @group_name
    # This is a class variable. Data type of this variable is "string". It is used to store name of group. Maximum length of string allowed to store in it is 1000. 
    group_name = models.CharField(max_length=1000, blank=True, null=True)
    def __unicode__(self):
        return self.group_name

class Assigned_question(models.Model):
    ## @var assignment_id
    # This is Foreign key. It is a reference to an assignment.
    assignment_id = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    ## @var question_id
    # This is Foreign key. It is a reference to a question.
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    def __unicode__(self):
        #return 'Object: '+str(self.pk)
        return 'Object: '+self.assignment_id.assignment_name+'---'+self.question_id.question_text

class Assigned_group(models.Model):
    ## @var assignment_id
    # This is Foreign key. It is a reference to an assignment.
    assignment_id = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    ## @var group_id
    # This is Foreign key. It is a reference to a group.
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    def __unicode__(self):
        return 'Object: '+self.group_id.group_name+'---'+self.assignment_id.assignment_name

class Group_member(models.Model):
    ## @var group_id
    # This is Foreign key. It is a reference to a group.
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    ## @var user_id
    # This is Foreign key. It is a reference to a user.
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    def __unicode__(self):
        return 'Object: '+self.group_id.group_name+'---'+self.user_id.username

class Assignment_log(models.Model):
    ## @var assignment_id
    # This is Foreign key. It is a reference to an assignment.
    assignment_id = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    ## @var user_id
    # This is Foreign key. It is a reference to a user.
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ## @var due_date
    # This is a class variable. Data type of this variable is "string". It is used to store due date for the assignment.
    due_date = models.CharField(max_length = 200, blank=True, null=True)
    ## @var finish_date 
    # This is a class variable. Data type of this variable is "string". It is used to store completion date for the assignment.
    finish_date = models.CharField(max_length = 200, blank=True, null=True)
    ## @var group_id
    # This is Foreign key. It is a reference to a group.
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    def __unicode__(self):
        return 'Object: '+ self.assignment_id.assignment_name+'---'+self.user_id.username+'---'+self.group_id.group_name
 
class Dataset(models.Model):
    ## @file_name
    # This is a class variable. Data type of this variable is "string". It is used to store name of file which contains dataset. Maximum length of string allowed to store in it is 200.
    file_name = models.CharField(max_length=200, blank=True, null=True)
    ## @file_location
    # This is a class variable. Data type of this variable is "string". It is used to store location of file. Maximum length of string allowed to store in it is 1000.
    file_location = models.CharField(max_length=1000, blank=True, null=True)
    ## @var uploader_id
    # This is Foreign key. It is a reference to a user.
    uploader_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ## @var upload_date
    # This is a class variable. Data type of this variable is "string". It is used to store date at which dataset was uploaded.
    upload_date = models.CharField(max_length=200, blank=True, null=True)
    def __unicode__(self):
        return self.file_name
