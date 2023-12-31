# -*- coding: utf-8 -*-
"""
Django views for ucs project.
This contains various function which process HTTP requests and render corrosponding html pages.
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os, time, zipfile, urllib, shutil, base64, json, hashlib, csv, math, platform
from time import strftime
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from .models import User, Question, Group_member, Group, Category, Dataset, Assignment, Assigned_group, Assigned_question, Assessment, Assignment_log
from .tools import date_norm, date_by_slash, get_timestamp, rmv_timestamp
from collections import defaultdict
from datetime import datetime, timedelta

#from osgeo import gdal
ErrorA = { 0 : "Insuficcient data for the assessment, missing NumOfPairs, Operator, or DateOfAssessment in row ",
1 : "Number of choices cannot be equal to 1 (allowed options are 0 or greater than 1) for entry located in row ",
2 : "Number of pairs needs to be same as the number of choices for entry located in row ",
3 : "The number of data points read is different than the number of data points specified in the file, row  ",
4 : "For a continuous distribution question the value assigned for operator should be LE or GE, row ",
5 : "For a continuous distribution question with a LE operator, with increasing probabilities the assigned values should be increasing, row ",
6 : "For a continuous distribution question with a GE operator, with increasing probabilities the assigned values should be decreasing, row ",
7 : "For a continuous distribution question the probabilities  assigned should fall between 0 and 1, row ",
8 : "For a multiple choice question the value assigned for operator should be EQ, row ",
9 : "For multiple choice questions the probabilities assigned should fall between 0 and 1, row ",
10 : "For multiple choice questions the value assigned should fall between 1 and the specified number of choices, row "}

WarningA ={0: "For multiple choice questions the sum of the assigned probabilites should add up to 1, row ",
1 : "The assessment details were updated for record in row ",
2 : "The assessment details reported in the import file is different than the one in the database for record in row "}

ErrorQ = {0 : "Question ID could not be found in the database for entry located in row ",
1 : "Mising fields or Number of choices cannot be equal to 1 (allowed options are 0 or greater than 1) for entry located in row"}

WarningQ = {0 : "The true value was updated for record in row ",
1 : "Insufficient data for the question, missing Question text, Category, NoOfChoices",
2 : "The units were updated for record in row ",
3 : "The units reported in the import file is different than the one in the database for record in row ",
4 : "A new category was created for record in row ",
5 : "Assignment name not found in the database "}

if 'Windows' in platform.system():
    file_path = os.path.join(os.getcwd(), "data")
    log_path  = 'tmp/log.csv'
    data_path = 'tmp/data.csv'
else:
    file_path = os.path.join("/home/shared/Apache", "data") #Uncommnet this when complete fixing
    log_path  = '/tmp/log.csv'
    data_path = '/tmp/data.csv'


def refresh_database():
    #####################SCRIPT TO CLEAN DATE###########################
    print "Start refreshing..."
    qid_list = Question.objects.all().values_list('id', flat=True)
    for qid in qid_list:
        close_date  = date_norm(Question.objects.get(id=qid).close_date)
        print close_date
        upload_date = date_norm(Question.objects.get(id=qid).upload_date)
        print upload_date
        Question.objects.filter(id=qid).update(close_date=close_date)
        Question.objects.filter(id=qid).update(upload_date=upload_date)
    aid_list = Assessment.objects.all().values_list('id', flat=True)
    timestamp = get_timestamp()
    for aid in aid_list:
        date_of_assessment = date_norm(Assessment.objects.get(id=aid).date_of_assessment)
        print date_of_assessment
        Assessment.objects.filter(id=aid).update(date_of_assessment=date_of_assessment, time_of_assessment=timestamp)
    sid_list = Assignment.objects.all().values_list('id', flat=True)
    for sid in sid_list:
        due_date = date_norm(Assignment.objects.get(id=sid).due_date)
        print due_date
        Assignment.objects.filter(id=sid).update(due_date=due_date)
    lid_list = Assignment_log.objects.all().values_list('id', flat=True)
    for lid in lid_list:
        due_date = date_norm(Assignment_log.objects.get(id=lid).due_date)
        print due_date
        Assignment_log.objects.filter(id=lid).update(due_date=due_date)
        finish_date = date_norm(Assignment_log.objects.get(id=lid).finish_date)
        print finish_date
        if not finish_date:
            Assignment_log.objects.filter(id=lid).update(finish_date="0000-00-00")
        else:
            Assignment_log.objects.filter(id=lid).update(finish_date=finish_date)
    bid_list = Dataset.objects.all().values_list('id', flat=True)
    for bid in bid_list:
        upload_date = date_norm(Dataset.objects.get(id=bid).upload_date)
        print upload_date
        Dataset.objects.filter(id=bid).update(upload_date=upload_date)
    print "End refreshing..."
    ####################################################################


def refresh_database_2():
    #####################SCRIPT TO CLEAN DATE###########################
    print "Start refreshing..."
    aid_list = Assessment.objects.all().values_list('id', flat=True)
    a_set    = Assignment.objects.get(assignment_name="Default")
    for aid in aid_list:
        Assessment.objects.filter(id=aid).update(assignment_id=a_set)
    print "End refreshing..."
    ####################################################################



def init_config():
    #Create an DEFAULT category
    c_set = Category.objects.all()
    if not c_set:
        default_category = Category(category_text = "Default", num_of_question = 0)
        default_category.save()

    #Create DEFAULT assignment
    #a_set = Assignment.objects.filter(assignment_name = "Default")
    #print "#$#$#@$@#$@"
    #print len(a_set), a_set
    #if len(a_set) == 0:
    #    default_assignment = Assignment(assignment_name = "Default", due_date = "")
    #    default_assignment.save()

    #Create ALL USERS group
    g_set = Group.objects.all()
    print "#$#$#@$@#$@"
    print len(g_set), g_set
    if not g_set:
        all_users_group = Group(group_name = "All Users")
        all_users_group.save()

    #Create NO USERS group
    g_set = Group.objects.filter(group_name = "No Users")
    print "#$#$#@$@#$@"
    print len(g_set), g_set    
    if len(g_set) == 0:
        no_users_group = Group(group_name = "No Users")
        no_users_group.save()

    #Create association between DEFAULT assignment and NO USERS group
    #default_assignment = Assignment.objects.get(assignment_name = "Default")
    #no_users_group = Group.objects.get(group_name = "No Users")
    #default_no_users = Assigned_group(assignment_id = default_assignment, group_id = no_users_group)
    #default_no_users.save()



## Function to render home-page.
# Function for rendering home page. Home page is rendered when someone login successfully.
def home_page(request):
    #refresh_database()
    ####init_config()
    ####refresh_database_2()
    ###print [item.pk for item in Assignment.objects.all()]
    ###print Assignment.objects.get(assignment_name="Default").id
    #DJ Home page to do report
    if "userId" in request.session.keys():
        user_name = request.session.get("userId")
        QA_id   = [] #Queation  or Assignment ID
        QA_type = [] #Question  or Assignment
        names   = [] #question text or assignment name
        f_dates = [] #due dates
        r_days  = [] #days left remaining
        groups  = [] #Group
        users   = [] #username
        now = datetime.now()
        #Check if admin
        current_user = User.objects.get(id= user_name)
        if current_user.admin_user==True:
            user_work = Assignment_log.objects.filter(user_id = current_user)
            #Loop through user assignments
            for uw in user_work:
                days_left = 'N/A'
                time = "E" #For error, no / or - in date to split
                if uw.due_date:
                    if '/' in uw.due_date:
                        time = uw.due_date.split("/")
                        s_date = datetime(int(time[2]), int(time[0]), int(time[1]))
                    elif '-' in uw.due_date:
                        time = uw.due_date.split("-")
                        s_date = datetime(int(time[0]), int(time[1]), int(time[2]))
                    if len(time) >= 3 and time != "E":
                        n_date = datetime(int(now.year), int(now.month), int(now.day))
                        delta  = s_date - n_date
                        days_left = delta.days
                if days_left == 0:
                    days_left = 1
                if uw.finish_date != "0000-00-00":
                    #print uw.assignment_id.assignment_name
                    if uw.due_date != "" and days_left < 0:   
                        continue
                    elif uw.due_date == "":
                        continue
                    r_days.append(days_left)
                else:
                    if days_left < 0:
                        continue
                    else:
                        r_days.append(days_left)
                QA_id.append(uw.assignment_id.id)
                QA_type.append("Assignment")
                names.append(uw.assignment_id.assignment_name)
                f_dates.append(uw.due_date)
                groups.append(uw.group_id.group_name)
                users.append(uw.user_id.username)
            question_work = Question.objects.filter(true_value__isnull = False).filter(true_value__exact='')
            for qw in question_work:
                days_left = 'N/A'
                time = "E" #For error, no / or - in date to split
                if qw.close_date:
                    if '/' in qw.close_date:
                        time = qw.close_date.split("/")
                    elif '-' in qw.close_date:
                        time = qw.close_date.split("-")
                    if len(time) >= 3 and time != "E":
                        s_date = datetime(int(time[0]), int(time[1]), int(time[2]))
                        n_date = datetime(int(now.year), int(now.month), int(now.day))
                        delta = s_date - n_date
                        days_left = delta.days
                if days_left == 0:
                    days_left = 1
                QA_id.append(qw.id)
                QA_type.append("Question")
                names.append(qw.question_text)
                f_dates.append(qw.close_date)
                r_days.append(days_left)
                groups.append("")
                users.append("Admin")
        else :
            #Regular User
            user_work = Assignment_log.objects.filter(user_id = user_name)
            #Loop through user assignments
            for uw in user_work:
                days_left = 'N/A'
                time = "E" #For error, no / or - in date to split
                if uw.due_date:
                    if '/' in uw.due_date:
                        time = uw.due_date.split("/")
                        s_date = datetime(int(time[2]), int(time[0]), int(time[1]))
                    elif '-' in uw.due_date:
                        time = uw.due_date.split("-")
                        s_date = datetime(int(time[0]), int(time[1]), int(time[2]))
                    if len(time) >= 3 and time != "E":
                        n_date = datetime(int(now.year), int(now.month), int(now.day))
                        delta  = s_date - n_date
                        days_left = delta.days
                if days_left == 0:
                    days_left = 1
                if uw.finish_date != "0000-00-00":
                    if uw.due_date != "" and days_left < 0:   
                        continue
                    elif uw.due_date == "":
                        continue
                    r_days.append(days_left)
                else:
                    if days_left < 0:
                        continue
                    else:
                        r_days.append(days_left)
                f_dates.append(uw.due_date)
                names.append(uw.assignment_id.assignment_name)
                QA_type.append("Assignment")
                QA_id.append(uw.assignment_id.id)
                groups.append(uw.group_id.group_name)
                users.append(uw.user_id.username)
        #Create list of table data
        dataList = [{"id":i, "type": t, "name": n, "due_date": dd, "days_left": dl, "group":g, "user":u} for i, t, n, dd, dl, g, u in zip(QA_id, QA_type, names, f_dates, r_days, groups, users)]
        json_data = json.dumps(dataList)
        return render(request, "ucs/home_page.html", {"dataList": json_data})
    else:
        return redirect(reverse("login"))


## Function to render information page
#
def info_page(request):
    return render(request, "ucs/info_page.html", {})


def register(request):
    message = None
    status = "success"
    if request.method == "POST":
        username = request.POST.get("username").lower().strip()
        email = request.POST.get("email", "").lower().strip()
        password = request.POST.get("password")
        existUser = User.objects.filter(email=email)
        existEmail = User.objects.filter(username=username)
        if existUser.exists():
            message = "This Email already exists. Please change it."
            status = "error"
        elif existEmail.exists():
            message = "This Username already exists. Please change it."
            status = "error"
        else:
            newUser = User(username=username, email=email, password=password)
            newUser.save()
            init_config() #Initialize default assignments, groups, and categories
            all_users = Group.objects.get(group_name = "All Users")
            new_user = User.objects.get(username = username)
            newMember = Group_member(group_id = all_users, user_id = new_user)
            newMember.save()
            message = "You successfully registered! Now login!"
    return render(request, "ucs/register.html", {"message" : message, "status": status})


def login(request):
    message = None
    status = None
    if request.method == "POST":
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        try:
            user = User.objects.get(email=email.lower())
            password_instore = user.password
            encryption = hashlib.md5()
            encryption.update(password_instore)
            password_md5 = encryption.hexdigest()
            if password == password_md5:
                request.session["userId"] = user.id
                request.session["username"] = user.username
                request.session["admin_user"] = user.admin_user
                return redirect(reverse("home_page"))
            else:
                message = "Wrong email or password."
                status = "error"
        except User.DoesNotExist:
            message = "Wrong email or password."
            status = "error"
    return render(request, "ucs/login.html", {"message":message, "status": status})


def retrieve(request):
    message = None
    email = request.POST.get("email", "")
    if request.method == "POST":
        try:
            user = User.objects.get(email=email.lower())
            password = user.password
            send_mail(
                    'Get back your password.',
                    'Your password: ' + password,
                    'apasys@outlook.com',
                    [email],
                    fail_silently=False,
            )
        except User.DoesNotExist:
            pass
        message = "Your password was sent to your email."
    return render(request, "ucs/retrieve.html", {"message":message, "status":"success"})


def logout(request):
    request.session.flush()  #remove all the data stored in session
    return redirect(reverse("login"))


def create_question(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    message = None

    tag_set = Category.objects.all()
    category_list = []
    number_list = []
    for item in tag_set:
        category_list.append(item.category_text)
        number_list.append(item.num_of_question)
    category_pair = [{"category_list":g, "number":n} for g, n in zip(category_list, number_list)]
    json_group = json.dumps(category_pair)
    data = {'rep_message': "hello"}
    if request.method == "POST":
        question_text = request.POST.get("question_text")
        exsitQuestion = Question.objects.filter(question_text = question_text)
        if exsitQuestion.exists():
            message = "This Question already exists. Please change it."
            status = "error"
            data['rep_message'] = 'Creation Failed: An Question with this title already exists.'
            data['status'] = False
            return JsonResponse(data)
        else:
            question_description = request.POST.get("question_description","")
            uploader = request.POST.get("uploader")
            question_source = request.POST.get("question_resource")
            category = request.POST.get("category")
            true_value = request.POST.get("true_value")
            forecast = request.POST.get("forecast")
            question_type = request.POST.get("question_type")
            question_purpose = request.POST.get("question_purpose")
            T_or_F = request.POST.get("true_or_false")
            allow_assessment = request.POST.get("allow_assessment")
            unit = request.POST.get("unit", "NA")
            upload_date = date_norm(request.POST.get("upload_date"))
            closing_date = request.POST.get("closing_date")
            print("question_type: "+question_type)
            print("forecast: "+forecast)
            print("question_purpose: "+question_purpose)
            print("allow_assessment: "+allow_assessment)
            is_discrete = True;
            is_forecast = True;
            is_trainning = True;
            is_assessment = True;
            num_of_choices = int(T_or_F)
            is_discrete = True if question_type == '1' else False
            is_forecast = True if forecast == '1' else False
            is_trainning = True if question_purpose == '1' else False
            is_assessment = True if allow_assessment == '1' else False
            upload_user = User.objects.get(username = uploader)
            cata = Category.objects.get(category_text = category)
            cata.num_of_question = cata.num_of_question+1
            cata.save()

            newQuestion = Question(
                question_text = question_text,
                uploader_id = upload_user,
                upload_date = upload_date,
                close_date = closing_date,
                question_description = question_description,
                question_source = question_source,
                category = cata,
                question_type = is_discrete,
                forecast = is_forecast,
                corporate_training = is_trainning,
                true_value = true_value,
                allow_assessment = is_assessment,
                num_of_choices = num_of_choices,
                unit = unit
            )
            newQuestion.save()
            #Update "ALL" category
            data['rep_message'] = 'Success'
            data['status'] = True
            return JsonResponse(data)
    return render(request, "ucs/create_question.html",{"message": message, "username": request.session.get("username"), "dataList": json_group})


def edit_question(request):
    user_id = request.session.get("userId")
    if not user_id:
        return render(request, "ucs/login.html")

    cata_set = Category.objects.all()
    cata_list = []
    for cn in cata_set:
        cata_list.append(cn.category_text)
    cata_data = [{"category": c} for c in cata_list]
    json_cata = json.dumps(cata_data)

    q_id = request.GET.get('question_id','')
    q_id = int(q_id)
    print q_id
    question   = Question.objects.get(id=q_id)
    close_date = date_by_slash(question.close_date)
    owned = False
    if user_id != question.uploader_id:
        owned = True
    return render(request, "ucs/edit_question.html", {"question":question, "userId": user_id, "uploaderId": question.uploader_id, "owned": owned, "username":request.session.get("username"), "cataList": json_cata, "close_date":close_date})


def search_question(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))

    questionSet = Question.objects.all()  #complex lookups with Q objects
    qidList = []
    questionList = []
    categoryList = []
    forecastList = []
    q_use_List = []
    q_type_List = []
    num_cho_List = []
    CloseTimeList = []
    #Remove the files that are not accessible (deleted or not mounted)
    for question in questionSet:
        qidList.append(question.id)
        questionList.append(question.question_text)
        categoryList.append(question.category.category_text)
        forecastList.append(question.forecast)
        q_type_List.append(question.question_type)
        q_use_List.append(question.corporate_training)
        num_cho_List.append(question.num_of_choices)
        CloseTimeList.append(question.close_date)

    existCate = Category.objects.all()
    Catelist = []
    for categories in existCate:
        Catelist.append(categories.category_text)
    json_user = json.dumps(Catelist)

    question_pair = [{"question_id":i, "question_text":a, "category_text":b, "end_time":e, "q_type":t, "q_use":u, "num_co":c, "forecast":f} for i, a, b, e, t, u, c, f in zip(qidList, questionList, categoryList, CloseTimeList, q_type_List, q_use_List, num_cho_List, forecastList)]
    json_group = json.dumps(question_pair)

    if request.method == 'POST':
        if request.POST['action'] == "delete":
            q_id = request.POST['question_id']
            Question.objects.get(id=q_id).delete()
    return render(request, "ucs/search_question.html", {"dataList": json_group,"catelist":json_user, "username": request.session.get("username")})


def save_question(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    if request.method=="POST":
        question_id = request.POST.get("question_id")
        unit = request.POST.get("unit")
        true_value = request.POST.get("true_value")
        category = request.POST.get("category")
        allow_assessment = request.POST.get("allow_assessment");
        category_info = Category.objects.get(category_text = category)
        date_true_value_known = request.POST.get("date_true_value_known")
        question_text = request.POST.get("question_text")
        question = Question.objects.get(id = question_id)
        question.unit = unit
        question.true_value = true_value
        question.category_id = category_info.id
        question.close_date = date_norm(date_true_value_known)
        question.question_text = question_text
        question.allow_assessment = allow_assessment
        question.save()
    return HttpResponse("success")


def create_assignment(request):
    message = None
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    elif request.method == 'POST':
        email_list = []
        all_users = []
        data = {}
        assignment_name = request.POST['assignment_name']
        assigned_date = request.POST['closing_date']
        assigned_group = request.POST.getlist('agroup[]')
        assigned_question = request.POST.getlist('aquestion[]')
        print assigned_group
        #Build Email List DJ
        for ag in assigned_group:
            group_info = Group.objects.filter(group_name = ag)
            user_list = Group_member.objects.filter(group_id = group_info)
            for ul in user_list:
                if ul.user_id not in all_users:
                    all_users.append(ul.user_id)
                    get_email = User.objects.get(username=ul.user_id)
                    if get_email.email not in email_list:
                        email_list.append(get_email.email)
        exsitAssignment = Assignment.objects.filter(assignment_name = assignment_name)
        print exsitAssignment
        print exsitAssignment.exists()
        strippedString = assignment_name.strip()
        #data = {'rep_message': assigned_group}
        #return JsonResponse(data)
        if strippedString == '':
            data['rep_message'] = 'Creation Failed: Empty Assignment Name.'
            data['status'] = False
            #return JsonResponse(data)
        elif exsitAssignment.exists():
            message = "This Assignment name already exists. Please change it."
            status = "error"
            data['rep_message'] = 'Creation Failed: An Assignment with this Name already exists.'
            data['status'] = False
            #return JsonResponse(data)
        elif assigned_question == []:
            data['rep_message'] = 'Creation Failed: No Question Selected.'
            data['status'] = False
            #return JsonResponse(data)
        elif assigned_group == []:
            data['rep_message'] = 'Creation Failed: No Group Selected.'
            data['status'] = False
            #return JsonResponse(data)
        else:
            message = "You successfully registered! Now login!"
            data['rep_message'] = 'Successfully Create Assignment. Redirect you to the Assignment List'
            data['status'] = True
            data['emails'] = email_list
            data['assignment_name'] = assignment_name

            newAssignment = Assignment(assignment_name = assignment_name, due_date = assigned_date)
            newAssignment.save()
            assignment_info = Assignment.objects.get(assignment_name = assignment_name)
            #assignment_id = assignment_info.id;
            for item in assigned_group:
                #item = item.encode("ascii")
                item = item.encode("utf-8")
                print(item)
                group_info = Group.objects.get(group_name = item)
                #group_id = group_info.id;
                newAssignedGroup = Assigned_group(assignment_id = assignment_info, group_id = group_info)
                newAssignedGroup.save()
            for q_id in assigned_question:
                #q_text = q_text.encode("utf-8")
                print(q_id)
                q_id = int(q_id)
                question_info = Question.objects.get(id = q_id)
                newAssignedQuestion = Assigned_question(assignment_id = assignment_info, question_id = question_info)
                newAssignedQuestion.save()
            #Insert into assignment list table without the finish_date
            for uid in all_users:
                insertIntoAssignmentLog = Assignment_log(assignment_id = assignment_info, user_id = uid, due_date = assigned_date,
                        finish_date = "0000-00-00", group_id = group_info)
                insertIntoAssignmentLog.save()
        return JsonResponse(data)
    else:
        ###################################
        existGroup = Group.objects.all()
        grouplist = []
        for group in existGroup:
            grouplist.append(group.group_name)
        json_group = json.dumps(grouplist)
        questionSet = Question.objects.all()  #complex lookups with Q objects
        qidList = []
        questionList = []
        categoryList = []
        forecastList = []
        q_use_List = []
        q_type_List = []
        num_cho_List = []
        CloseTimeList = []
        uploaderList = []
        #Remove the files that are not accessible (deleted or not mounted)
        for question in questionSet:
            qidList.append(question.id)
            questionList.append(question.question_text)
            categoryList.append(question.category.category_text)
            forecastList.append(question.forecast)
            q_type_List.append(question.question_type)
            q_use_List.append(question.corporate_training)
            num_cho_List.append(question.upload_date)
            CloseTimeList.append(question.close_date)
        question_pair = [{"question_id":i, "question_text":a, "category_text":b, "end_time":e, "up_date":u} for i, a, b, e, u in zip(qidList, questionList, categoryList, CloseTimeList, num_cho_List)]
        json_question = json.dumps(question_pair)
        ###################################
        return render(request, "ucs/create_assignment.html", {"dataList": json_question, "message": message, "initialItems": json_group})


def manage_category(request):
    tag_set = Category.objects.all()
    cidList = []
    category_list = []
    number_list = []
    for item in tag_set:
        cidList.append(item.id)
        category_list.append(item.category_text)
        filtered_question = Question.objects.filter(category = item)
        if item.num_of_question != len(filtered_question):
            item.num_of_question = len(filtered_question)
            item.save()
        else:
            pass
        number_list.append(item.num_of_question)
    category_pair = [{"category_id":i, "category":g, "number":n} for i, g, n in zip(cidList, category_list, number_list)]
    print category_pair
    json_group = json.dumps(category_pair)

    if request.method == "POST":
        c_id = request.POST.get("category_id")
        if request.POST['action'] == "delete":
            Category.objects.get(id = c_id).delete()
        elif request.POST['action'] == "add":
            data = {'rep_message': "None", 'status': False}
            category_text = request.POST.get("category_text")
            exsit_cate = Category.objects.filter(category_text = category_text)
            if exsit_cate.exists():
                data['rep_message'] = 'Same category exist'
                data['status'] = False
            elif not category_text:
                data['rep_message'] = 'Category name cannot be empty'
                data['status'] = False
            else:
                New_category = Category(category_text = category_text, num_of_question = 0)
                New_category.save()
                data['rep_message'] = 'Successful creating category'
                data['status'] = True
            return JsonResponse(data)
    return render(request, "ucs/search_category.html", {"username": request.session.get("username"), "dataList": json_group})


def search_assignment(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    message = None

    existAssignment = Assignment.objects.all()
    aidList = []
    assignmentlist = []
    qnumber = []
    #DJ show closing date and finish date
    asgnCD = [] # closing dates
    for assignment in existAssignment:
        aidList.append(assignment.id)
        number = Assigned_question.objects.filter(assignment_id = assignment).count()
        if number == 0 and assignment.assignment_name != "Default":
            assignment.delete()
        else:
            assignmentlist.append(assignment.assignment_name)
            qnumber.append(number)
            asgnCD.append(assignment.due_date)
    at_pair = [{"assignment_id":i, "assignment_name":g, "number":n, "cdate":c} for i, g, n, c in zip(aidList, assignmentlist, qnumber, asgnCD)]
    json_assignment = json.dumps(at_pair)
    if request.method == 'POST':
        if request.POST['action'] == "delete":
            a_id = request.POST['assignment_id']
            assignment = Assignment.objects.get(id = a_id)
            #for assignment in existAssignment:
            Assigned_question.objects.filter(assignment_id = assignment).delete()
            Assigned_group.objects.filter(assignment_id = assignment).delete()
            assignment.delete()
            Assignment_log.objects.filter(assignment_id = assignment).delete()

    return  render(request, "ucs/search_assignment.html", {"message": message, "username": request.session.get("username"), "dataList": json_assignment})


def show_assignment(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    message = None

    affiliatedGroup = Group_member.objects.filter(user_id = user_id)
    #print affiliatedGroup
    existAssignment = []
    for group in affiliatedGroup:
        groupAssignments = Assigned_group.objects.filter(group_id = group.group_id)
        for assignment in groupAssignments:
            existAssignment.append(assignment.assignment_id)
    aidList = []
    assignmentlist = []
    qnumber = []
    #DJ Remove assignments from the manage page that are past the closeing date
    now = datetime.now()
    n_date = datetime(int(now.year), int(now.month), int(now.day))
    daysLeft = []
    #DJ show closing date and finish date
    asgnCD = [] # closing dates
    asgnFD = [] # Finish dates
    for assignment in existAssignment:
        #Split the date, check for / or - because of format changes
        time = 'E' #For error checking and empty close dates
        days_left = 'E'
        if '/' in assignment.due_date:
            time = assignment.due_date.split("/")
            s_date = datetime(int(time[2]), int(time[0]), int(time[1]))
        elif '-' in assignment.due_date:
            time = assignment.due_date.split("-")
            s_date = datetime(int(time[0]), int(time[1]), int(time[2]))
        if len(time) >= 3 and time != "E":
            n_date = datetime(int(now.year), int(now.month), int(now.day))
            delta  = s_date - n_date
            days_left = delta.days
        #Check to see if a assignment has been solved
        user_work = Assignment_log.objects.filter(assignment_id = assignment.id).filter(user_id = user_id)
        #print assignment.assignment_name
        #print "****"
        finish_date = ""
        for uw in user_work:
            finish_date = uw.finish_date
            if uw.finish_date != "0000-00-00":
                if uw.due_date != "" and days_left < 0:
                    days_left = 's'
                    break
                elif uw.due_date == "":
                    days_left = 's'
                    break
            break
        asgnCD.append(assignment.due_date)
        asgnFD.append(finish_date)
        daysLeft.append(days_left)
        #print assignment.assignment_name
        #print days_left
        #if days_left < 0 or days_left == 'E':
        #    continue
        #End of past due assignment filtering
        aidList.append(assignment.id)
        assignmentlist.append(assignment.assignment_name)
        number = Assigned_question.objects.filter(assignment_id = assignment).count()
        qnumber.append(number)
    at_pair = [{"assignment_id":i, "assignment_name":g, "number":n, "daysleft":d, "cdate":c, "fdate":f } for i, g, n, d, c, f in zip(aidList, assignmentlist, qnumber, daysLeft, asgnCD, asgnFD)]
    json_assignment = json.dumps(at_pair)
    return  render(request, "ucs/show_assignment.html", {"message": message, "username": request.session.get("username"), "dataList": json_assignment})


def edit_assignment(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    #%$%$%$%$%$%$%$%$%$%$
    if request.method == 'POST':
        a_id = request.POST['assignment_id']
        a_id = int(a_id)
        #print 'Assignment id: ', a_id
        target_assignment = Assignment.objects.get(id = a_id)
        due_date = Assignment.objects.get(id = a_id).due_date
        #due_date = ""
        #for cw in Assignment.objects.filter(id = a_id):
        #    due_date = cw.due_date
        #    break
        a_name = target_assignment.assignment_name
        print 'Assignment name: ', a_name
        #DJ - Make sure new users or delted users update the assignment_log table
        if request.POST['action'] == "delete":
            g_name = request.POST['gp_name']
            # target_group is the group that needs to be added
            target_group = Group.objects.filter(group_name = g_name)
            get_groups = Assigned_group.objects.filter(assignment_id = target_assignment)
            usrList = []
            for grp in get_groups:
                if grp.group_id != target_group.first():
                    get_usrList = Group_member.objects.filter(group_id = grp.group_id)
                    for g_uL in get_usrList:
                        usrList.append(g_uL.user_id)
            get_users = Group_member.objects.filter(group_id = target_group)
            for duser in get_users:
                if duser.user_id not in usrList:
                    Assignment_log.objects.filter(user_id = duser.user_id, assignment_id = target_assignment).delete()
            Assigned_group.objects.filter(assignment_id = target_assignment, group_id = target_group).delete()
            #delete_users = Group_member.objects.filter(group_id = target_group)
        if request.POST['action'] == "add":
            add_group = request.POST.getlist('gp_name[]')
            due_date  = date_norm(request.POST['closing_date'])

            Assignment.objects.filter(id = a_id).update(due_date = due_date)
            Assignment_log.objects.filter(assignment_id = target_assignment).update(due_date = due_date)

            curr_users_list = []
            user_list = Assignment_log.objects.filter(assignment_id = target_assignment)
            for curr_user in user_list:
                curr_users_list.append(curr_user.user_id)

            for item in add_group:
                item = item.encode("utf-8")
                target_group = Group.objects.get(group_name = item)
                
                user_new = Group_member.objects.filter(group_id = target_group)
                for newuser in user_new:
                    if newuser.user_id not in curr_users_list:
                        print "adding user"
                        print newuser
                        insertIntoAssignmentLog = Assignment_log(assignment_id = target_assignment, user_id = newuser.user_id, due_date = due_date,
                        finish_date = "0000-00-00", group_id = target_group)
                        insertIntoAssignmentLog.save()
                    newgroup = Assignment_log.objects.filter(group_id = target_group).filter(user_id = newuser.user_id)
                    if len(newgroup) == 0:
                        insertIntoAssignmentLog = Assignment_log(assignment_id = target_assignment, user_id = newuser.user_id, due_date = due_date,
                        finish_date = "0000-00-00", group_id = target_group)
                        insertIntoAssignmentLog.save()
                    #all_users.append(ul.user_id)
                newAssignedGroup = Assigned_group(assignment_id = target_assignment, group_id = target_group)
                newAssignedGroup.save()
    else:
        a_id = request.GET.get('assignment_id','')
        a_id = int(a_id)
        print 'Assignment id: ', a_id
        target_assignment = Assignment.objects.get(id = a_id)
        a_name   = target_assignment.assignment_name
        print 'Assignment name: ', a_name
        due_date = date_by_slash(target_assignment.due_date)
    #$$%$%$%$%$%$%$%$%$%$%
    question_in_assignment = Assigned_question.objects.filter(assignment_id = target_assignment)
    text_list = []
    cata_list = []
    question_type_list = []

    for item in question_in_assignment:
        question_text = item.question_id.question_text
        text_list.append(question_text)
        cata_text = item.question_id.category.category_text
        cata_list.append(cata_text)
        question_type = item.question_id.question_type
        if question_type == True:
            question_type_list.append("1")
        else:
            question_type_list.append("2")
    question_pair = [{"question_text":t, "cata_text":c, "question_type":y} for t, c, y in zip(text_list, cata_list, question_type_list)]
    print question_pair
    json_question = json.dumps(question_pair)
    group_in_assignment = Assigned_group.objects.filter(assignment_id = target_assignment)
    AllGroup = Group.objects.all()
    grouplist = []
    for group in AllGroup:
        exsit_in = Assigned_group.objects.filter(assignment_id = target_assignment, group_id = group)
        if not exsit_in:
            grouplist.append(group.group_name)
    json_group = json.dumps(grouplist)

    gidList = []
    exgrouplist = []
    for exgroup in group_in_assignment:
        group = exgroup.group_id;
        gidList.append(group.id)
        exgrouplist.append(group.group_name)

    at_pair = [{"group_id":i, "group_name":g} for i, g in zip(gidList, exgrouplist)]
    group_info = json.dumps(at_pair)
    return render(request, "ucs/edit_assignment.html", {"assignment_id":a_id, "assignment_name":a_name, "group_not_in_assignment":json_group, "group_in_assignment":group_info, "question_in_assignment":json_question, "due_date":due_date})


def do_assignment(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    if request.method == 'POST':
        data = {}
        print 'HERE '
        uploader = request.POST['uploader']
        target_user = User.objects.get(username = uploader)
        upload_date = datetime.today().strftime("%Y-%m-%d")
        answered_text = request.POST.getlist('question_text[]')
        answered_question = request.POST.getlist('answer[]')
        a_id = request.POST['assignment_id']
        a_id = int(a_id)
        target_assignment = Assignment.objects.get(id = a_id)
        assignment_name = target_assignment.assignment_name
        print 'assignment_name: ', assignment_name
        j = 0
        print answered_text
        print answered_question
        for item in answered_text:
            #print item
            q_text = item.encode("utf-8")
            filtered_question = Question.objects.get(question_text = q_text)
            if filtered_question.allow_assessment==False:
                continue
            if filtered_question.question_type:
                operator = 'EQ'
            else:
                operator = 'LE'
            q_answer = answered_question[j].encode("utf-8")
            print q_answer
            j = j+1
            content = q_answer.split(",")
            i = 0
            print "\n\n\n Content ",content
            if float(content[0]) > float(content[2]):
                operator = 'GE'
            print "Operator: ",operator
            timestamp = get_timestamp()
            while (i < len(content)):
                asst = content[i]
                option = str(float(asst))
                i = i + 1
                prob = content[i]
                answer = str(float(prob)/100.0)
                i = i + 1
                #operator = content[i]
                #i = i + 1
                #print operator
                ###JASON 06-17###
                new_assessment = Assessment(assignment_id = target_assignment, question_id = filtered_question, user_id = target_user, option_text = option, answer_text = answer, operator = operator, date_of_assessment = upload_date, time_of_assessment=timestamp)
                #new_assessment = Assessment(question_id = filtered_question, user_id = target_user, option_text = option, answer_text = answer, operator = operator, date_of_assessment = upload_date, time_of_assessment=timestamp)
                new_assessment.save()
        f_date = upload_date
        print 'f_date: ', f_date
        #DJ
        print 'assignment_name: ', assignment_name
        target_assignment = Assignment.objects.filter(assignment_name = assignment_name)
        print target_assignment
        print 'Update...'
        Assignment_log.objects.filter(assignment_id = target_assignment).filter(user_id = target_user).update(finish_date = f_date)
        print 'COMPLETE...'
        data['rep_message'] = 'Successfully Create Assessment. Redirect you to the Assignment List'
        data['status'] = True
        return JsonResponse(data)
    else:
        a_id = request.GET.get('assignment_id','')
        a_id = int(a_id)
        target_assignment = Assignment.objects.get(id = a_id)
        assignment_name = target_assignment.assignment_name
        print 'assignment_name: ', assignment_name
        assignment_set = Assigned_question.objects.filter(assignment_id = target_assignment)
        text_list = []
        description_list = []
        source_list = []
        question_type_list = []
        unit_list = []
        option_list = []

        for item in assignment_set:
            print(item)
            question_text = item.question_id.question_text
            text_list.append(question_text)
            question_description = item.question_id.question_description
            description_list.append(question_description)
            question_source = item.question_id.question_source
            source_list.append(question_source)
            unit = item.question_id.unit
            unit_list.append(unit)
            question_type = item.question_id.question_type
            true_or_false = item.question_id.num_of_choices
            option_list.append(true_or_false)
            if question_type == True:
                question_type_list.append("1")
            else:
                question_type_list.append("2")
        question_pair = [{"question_text":t, "question_description":d, "question_source":s,  "unit":u, "question_type":y, "num_of_choices":o} for t, d, s, u, y, o in zip(text_list,description_list, source_list,unit_list,question_type_list, option_list)]
        json_question = json.dumps(question_pair)
    return render(request, "ucs/do_assignment.html", {"assignment_title":assignment_name, "username": request.session.get("username"), "dataList": json_question})


#[Junqi] Updates
def create_group(request):
    message = None
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    existUser = User.objects.all()
    userlist = []
    for user in existUser:
        userlist.append(user.username)
    json_user = json.dumps(userlist)
    data = {'rep_message': "hello"}

    if request.method == 'POST':
        group_name = request.POST['gpname']
        gmember = request.POST.getlist('gmember[]')
        exsitGroup = Group.objects.filter(group_name = group_name)
        strippedString = group_name.strip()
        if strippedString == '':
            data['rep_message'] = 'Creation Failed: Empty Group Name.'
            data['status'] = False
            return JsonResponse(data)

        if gmember == []:
            data['rep_message'] = 'Creation Failed: No Group Member Selected.'
            data['status'] = False
            return JsonResponse(data)

        if exsitGroup.exists():
            message = "This group name already exists. Please change it."
            status = "error"
            data['rep_message'] = 'Creation Failed: A Group with this Name already exists.'
            data['status'] = False
            return JsonResponse(data)
        else:
            newGroup = Group(group_name = group_name)
            newGroup.save()
            group_id = newGroup.id
            for item in gmember:
                item = item.encode("utf-8")
                print(item)
                user_info = User.objects.get(username = item)
                user_id = user_info.id
                newAssignedGroup = Group_member(group_id = newGroup, user_id = user_info)
                newAssignedGroup.save()
            message = "You successfully registered! Now login!"
            data['rep_message'] = 'Successfully Create Group. Redirect you to the Group List'
            data['status'] = True
            return JsonResponse(data)
    return render(request, "ucs/create_group.html", {"message": message, "username": request.session.get("username"), "initialItems": json_user})


def search_group(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    message = None
    if request.method == 'POST':
        if request.POST['action'] == "delete":
            g_id = request.POST['group_id']
            target_group = Group.objects.get(id = g_id)
            Group_member.objects.filter(group_id = target_group).delete()
            target_group.delete()
    existGroup = Group.objects.all()
    gidList = []
    grouplist = []
    mnumber = []
    for group in existGroup:
        gidList.append(group.id)
        grouplist.append(group.group_name)
        number = Group_member.objects.filter(group_id = group).count()
        mnumber.append(number)
    gp_pair = [{"group_id":i, "group_name":g, "number":n} for i, g, n in zip(gidList, grouplist, mnumber)]
    json_group = json.dumps(gp_pair)

    return  render(request, "ucs/search_group.html", {"message": message, "username": request.session.get("username"), "dataList": json_group})


def edit_group(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    if request.method == 'POST':
        g_id = request.POST['group_id']
        g_id = int(g_id)
        target_group = Group.objects.get(id = g_id)
        if request.POST['action'] == "delete":
            u_name = request.POST['member_name']
            target_user = User.objects.filter(username = u_name)
            Group_member.objects.filter(group_id = target_group, user_id = target_user).delete()
        if request.POST['action'] == "add":
            g_user = request.POST.getlist('gmember[]')
            for u_name in g_user:
                u_name = u_name.encode("utf-8")
                target_user = User.objects.get(username = u_name)
                newAssignedGroup = Group_member(group_id = target_group, user_id = target_user)
                newAssignedGroup.save()
    else:
        g_id = request.GET.get('group_id','')
        g_id = int(g_id)
        target_group = Group.objects.get(id = g_id)
    gpname = target_group.group_name
    user_in_group = Group_member.objects.filter(group_id = target_group)
    AllUser = User.objects.all()
    userlist = []
    for user in AllUser:
        exist_in_group = Group_member.objects.filter(group_id = target_group, user_id = user)
        if not exist_in_group:
            userlist.append(user.username)
    json_user = json.dumps(userlist)

    exist_user_list = []
    exist_user_email = []
    for exist_user in user_in_group:
        target_user = exist_user.user_id;
        exist_user_list.append(target_user.username)
        exist_user_email.append(target_user.email)

    gp_pair = [{"user_name":g, "user_email":e} for g, e in zip(exist_user_list, exist_user_email)]
    user_info = json.dumps(gp_pair)

    return  render(request, "ucs/edit_group.html", {"group_id": g_id, "group_name": gpname, "user_not_in_group": json_user, "user_in_group": user_info})


def batch_import(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    message = ""
    new_assignment_list = []  #A list for the new assignment appeared in the file
    #print 'The user id is ', user_id
    if request.method == "POST":
        shift = 1 #The input file format change
        #Write the uploaded file to the Uploads folder on Terra
        fileData = request.FILES.get("file_data")
        file_name = fileData.name
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_location = os.path.join(file_path, file_name)
        msg_location = os.path.join(file_path, os.path.splitext(file_name)[0]+'_log.csv')
        with open(file_location, 'wb+') as destination:
            for chunk in fileData.chunks():
                destination.write(chunk)
        upload_user = User.objects.get(id = user_id)
        upload_date = strftime("%Y-%m-%d")

        print 'The file name is: ', file_name
        ds_obj = Dataset.objects.filter(file_name=file_name)
        if len(ds_obj) == 0:
            QBank = Dataset(file_name=file_name, file_location=file_location, uploader_id=upload_user, upload_date=upload_date)
            QBank.save()
        #print WarningQ[4]
        ##############################################RAUL'S CODE############################################
        ErrorLogQ = []
        WarningLogQ = []
        ErrorLogA = []
        WarningLogA = []
        reader = csv.reader(open(file_location),delimiter=",")
        header = next(reader)
        #print header, len(header), header.index("NUMBER OF PAIRS")
        data = []
        try:
            print header
            if "NUMBER OF PAIRS" in header and header.index("NUMBER OF PAIRS") == shift+15:
                for row in reader:
                    # If encounter an empty row, skip the rest of the lines
                    if not row:
                        break
                    ErrorQv = 0
                    WarningQv = 0
                    # ********************** QUESTION INFORMATION VALIDATION **********************
                    # Check and validate all the question information before it gets stored into the
                    # database. There are 2 associated errors with the question data that will prevent
                    # questions from being imported, while there are 5 warnings. A warning will
                    # still be able to store data in the database
                    #@
                    if ErrorQv == 0:
                        if row[shift+4] and row[shift+5] and row[shift+6]:
                            # VARIABLE NAME IN PYTHON  VARIABLE NAME IN DJANGO
                            # ADD A VALIDATION FOR QUESTIONS THAT ARE FORECAST
                            # [TODO] NEED TO CHANGE FINALIZE THE HEADING FORMAT
                            AssignmentName = str(row[shift+0])                                      ## assignment name *
                            #print 'AssignmentName:', AssignmentName
                            QuestionUse = str(row[shift+1])                                         ## training *
                            #print 'QuestionUse:', QuestionUse
                            QForecast = str(row[shift+2]).title()                                   ## forecast *
                            #print 'QForecast: ', QForecast
                            QuestionType = str(row[shift+3]).title()                                ## question_type *
                            #print 'QuestionType: ', QuestionType
                            NoOfChoices = int(row[shift+4])                                         ## num_of_choices *
                            #print 'NoOfChoices: ', NoOfChoices
                            QCategory = unicode(str(row[shift+5]).strip(), errors='replace')        ## category *
                            #print 'QCategory: ', QCategory
                            QuestionText = unicode(str(row[shift+6]).strip(), errors='replace')     ## question_text *
                            #print 'QuestionText: ', QuestionText
                            DateTrueValueKnown = date_norm(str(row[shift+7]))                       ## close_date *
                            #print "DateTrueValueKnown: ", DateTrueValueKnown;
                            TrueValue = unicode(str(row[shift+8]).strip(), errors='replace')        ## true_value *
                            #print 'TrueValue: ', TrueValue
                            Units = unicode(str(row[shift+9]).strip(), errors='replace')            ## unit *
                            #print 'Units: ', Units
                            QuestionSource = unicode(str(row[shift+10]).strip(), errors='replace')  ## question_source *
                            #print 'QuestionSource: ', QuestionSource
                            AllowAssessment = str(row[shift+11]).title()                            ## allow_assessment *
                            #print 'AllowAssessment: ', AllowAssessment
                        else:
                            ErrorQv+=1
                            ErrorLogQ.insert(reader.line_num, ErrorQ[1] + str(reader.line_num))
                        #print QCategory
                        #Check category exists in the database
                        Q = Category.objects.filter(category_text=QCategory)
                        if len(Q) == 0:
                            WarningQv +=1
                            WarningLogQ.insert(reader.line_num, WarningQ[4] + str(reader.line_num))
                            newCategory = Category(category_text=QCategory, num_of_question=0)
                            newCategory.save()
                        CategoryObj = Category.objects.get(category_text=QCategory)
                        
                        #Check assignment exists in the database
                        Q = Assignment.objects.filter(assignment_name=AssignmentName)
                        if len(Q) == 0:
                            if not AssignmentName:
                                AssignmentName = str(os.path.splitext(file_name)[0])+'_'+str(upload_date)
                            WarningQv +=1
                            WarningLogQ.insert(reader.line_num, WarningQ[5] + str(reader.line_num))
                            newAssignment  = Assignment(assignment_name=AssignmentName, due_date="")
                            newAssignment.save()
                            AssignmentObj  = Assignment.objects.get(assignment_name=AssignmentName)
                            no_users_group = Group.objects.get(group_name="No Users")
                            #insertIntoAssignmentLog = Assignment_log(assignment_id=AssignmentObj, user_id=upload_user, due_date=upload_date, 
                            #    finish_date="0000-00-00", group_id=no_users_group)
                            insertIntoAssignmentLog = Assignment_log(assignment_id=AssignmentObj, user_id=upload_user, due_date="", 
                                finish_date=upload_date, group_id=no_users_group)
                            insertIntoAssignmentLog.save()
                            ##############################
                            newAssignedGroup = Assigned_group(assignment_id=AssignmentObj, group_id=no_users_group)
                            newAssignedGroup.save()
                            ##############################
                            new_assignment_list.append(AssignmentName)
                        AssignmentID = Assignment.objects.get(assignment_name=AssignmentName)
                    if ErrorQv == 0:
                        # Check if question exists in database
                        QSet = Question.objects.filter(question_text = QuestionText)
                        if len(QSet) == 0:
                            # Question does not exist in the database add question
                            # UPDATE FIELDS
                            newQuestion = Question(question_text = QuestionText, uploader_id = upload_user, upload_date = upload_date,
                                close_date = DateTrueValueKnown, num_of_choices = NoOfChoices, category = CategoryObj,
                                question_type = QuestionType, forecast = QForecast, true_value = TrueValue, unit = Units,
                                question_source = QuestionSource, allow_assessment = AllowAssessment)
                            newQuestion.save()
                        # Question exists then update true value/units
                        else:
                            Q = Question.objects.get(question_text=QuestionText)
                            if TrueValue:
                                print 'TrueValueSystem: ', Q.true_value
                                if Q.true_value != TrueValue:
                                    Question.objects.filter(id=Q.id).update(true_value = TrueValue)
                                    WarningQv += 1
                                    WarningLogQ.insert(reader.line_num, WarningQ[0] + str(reader.line_num))
                            if Units:
                                print 'TrueUnitsSystem: ', Q.unit
                                if Q.unit == '':
                                    Question.objects.filter(id=Q.id).update(unit = Units)
                                    WarningQv +=1
                                    WarningLogQ.insert(reader.line_num, WarningQ[2] + str(reader.line_num))
                                elif Q.unit != Units:
                                    WarningQv +=1
                                    WarningLogQ.insert(reader.line_num, WarningQ[3] + str(reader.line_num))
                        QuestionID = Question.objects.get(question_text=QuestionText)
                        print 'QuestionID: ', QuestionID
                        # If the Assignment Name is first-time appeared in the file
                        if AssignmentName in new_assignment_list:
                            AQSet = Assigned_question.objects.filter(assignment_id=AssignmentID, question_id=QuestionID)
                            if len(AQSet) == 0:
                                newAssignedQuestion = Assigned_question(assignment_id=AssignmentID, question_id=QuestionID)
                                newAssignedQuestion.save()
                    # Does not allow the import of an Assessment unless the question information is available
                    if ErrorQv == 0:
                        ErrorAv = 0
                        WarningAv = 0
                    else:
                        WarningAv = 1
                    # ********************** ASSESSMENT INFORMATION VALIDATION **********************
                    # Check and validate all the assessment information before it gets stored into the
                    # database. There are 10 associated errors with the assessment data that will prevent
                    # assessments from being imported, while there is only 1 warning. A warning will
                    # still be able to store data in the database
                    #Make a comment regarding how this cant be empty
                    ImportAssessment = False
                    for i in range (12, 15):
                        if row[shift+i]:
                            ImportAssessment = True
                    if ImportAssessment == True:
                        DateOfAssessment = date_norm(str(row[shift+12]))
                        Operator = str(row[shift+13])
                        DetailsOfAssessment = str(row[shift+14])
                        #VALIDATION OF ASSESSMENT INPUT/OPTIONS
                        #Validate that NumOfPairs, Operator, or DateOfAssessment are not missing
                        if row[shift+15] == '' or Operator == '' or DateOfAssessment == '' or row[shift+4] == '':
                            ErrorAv += 1
                            ErrorLogA.insert(reader.line_num, ErrorA[0]+str(reader.line_num))
                        else:
                            NumOfPairs=int(row[shift+15])
                            NumOfChoices=float(row[shift+4])
                        if ErrorAv == 0:
                            # Validate that NumOfChoices can only be 0 or greater than 1
                            if NumOfChoices < 0 or NumOfChoices == 1:
                                ErrorAv +=1
                                ErrorLogA.insert(reader.line_num, ErrorA[1]+str(reader.line_num))
                            # Check for insufficient data when NumOfPairs is different than NumOfChoices for discrete
                            elif NumOfChoices == 0:
                                # Check that for the continuous case NumOfPairs is greater than 1
                                # Should a check for the case were continuous should be 0 for NumOfChoices
                                if NumOfPairs <= 0:
                                    ErrorAv += 1
                                    ErrorLogA.insert(reader.line_num, ErrorA[2]+str(reader.line_num))
                            else:
                                # Check that for discrete the NumOfChoices is equal to NumOfPairs
                                if NumOfPairs != NumOfChoices:
                                    ErrorAv +=1
                                    ErrorLogA.insert(reader.line_num, ErrorA[2]+str(reader.line_num))
                        if ErrorAv == 0:
                            #VALIDATION OF SUFFICIENT DATA
                            prob = []
                            val = []
                            for i in range(0, NumOfPairs):
                                if not row[shift+16+2*i] or not row[shift+17+2*i]:
                                    ErrorAv += 1
                                    ErrorLogA.insert(reader.line_num, ErrorA[3]+str(reader.line_num))
                                else:
                                    prob.insert(reader.line_num, float(row[shift+16+2*i]))
                                    val.insert(reader.line_num, float(row[shift+17+2*i]))
                        #VALIDATION OF AVAILABLE ASSESSMENT DATA
                        # Sort both Probabilities and Values for further validation if there are more than
                        # 2 pairs of assessments
                        if ErrorAv == 0:
                            if len(prob) > 2:
                                prob, val = (list(x) for x in zip(*sorted(zip(prob, val))))
                            if NumOfChoices > 1:
                                # Check that the operator is not different than EQ or empty
                                if Operator != "EQ":
                                    ErrorAv += 1
                                    ErrorLogA.insert(reader.line_num, ErrorA[8]+str(reader.line_num))
                                # Warn user that the sum is not 1
                                if sum(prob) != 1:
                                    WarningAv += 1
                                    WarningLogA.insert(reader.line_num, WarningA[0]+str(reader.line_num))
                                # Check that all probabilities are between 0 and 1
                                if sum([i > 1 for i in prob]) > 0:
                                    ErrorAv +=1
                                    ErrorLogA.insert(reader.line_num, ErrorA[9]+str(reader.line_num))
                                if sum([i < 0 for i in prob]) > 0:
                                    ErrorAv +=1
                                    ErrorLogA.insert(reader.line_num, ErrorA[9]+str(reader.line_num))
                                # Check that all values are between 1 and the NumOfChoices
                                if sum([i > NumOfChoices for i in val]) > 0:
                                    ErrorAv +=1
                                    ErrorLogA.insert(reader.line_num, ErrorA[10]+str(reader.line_num))
                                # Check that for LE everything is ascending
                                if Operator == "LE" and NumOfPairs > 2:
                                    if sum([x>y for x, y in zip(val, val[1:])]) > 0:
                                        ErrorAv +=1
                                        ErrorLogA.insert(reader.line_num, ErrorA[5]+str(reader.line_num))
                                # Check that for GE everything is ascending
                                elif Operator == "GE" and NumOfPairs > 2:
                                    if sum([x<y for x, y in zip(val, val[1:])]) > 0:
                                        ErrorAv +=1
                                        ErrorLogA.insert(reader.line_num, ErrorA[6]+str(reader.line_num))
                                # Check that the operator is EQ
                                elif Operator == "EQ" and NumOfPairs >= 2:
                                    pass
                                # Check that the operator is not EQ or empty
                                else:
                                    ErrorAv +=1
                                    ErrorLogA.insert(reader.line_num, ErrorA[4]+str(reader.line_num))
                                # Check that all probabilities are between 0 and 1
                                if sum([i > 1 for i in prob]) > 0:
                                    ErrorAv += 1
                                    ErrorLogA.insert(reader.line_num, ErrorA[7]+str(reader.line_num))
                                if sum([i < 0 for i in prob]) > 0:
                                    ErrorAv += 1
                                    ErrorLogA.insert(reader.line_num, ErrorA[7]+str(reader.line_num))
                        if ErrorAv == 0:
                            for i in range(0, NumOfPairs):
                                data.append([0, QuestionUse, QForecast, QuestionType, NoOfChoices, QCategory, QuestionText,
                                     DateTrueValueKnown, TrueValue, Units, QuestionSource, AllowAssessment,
                                     DateOfAssessment, Operator, DetailsOfAssessment, NumOfPairs, prob[i], val[i]])
                                ## Check if Assessment exists in database
                                timestamp = get_timestamp()
                                A = Assessment.objects.filter(assignment_id = AssignmentID
                                    ).filter(user_id = upload_user
                                    ).filter(question_id = QuestionID
                                    ).filter(answer_text = prob[i]
                                    ).filter(option_text = val[i]
                                    ).filter(date_of_assessment = DateOfAssessment
                                    ).filter(details_of_assessment = DetailsOfAssessment)
                                if len(A) == 0:
                                    #Assessment does not exist in the database add question
                                    ###JASON 06-17###
                                    newAssessment = Assessment(assignment_id=AssignmentID, question_id=QuestionID, user_id=upload_user, 
                                        answer_text=prob[i], option_text=val[i], operator=Operator, date_of_assessment=DateOfAssessment,
                                        time_of_assessment=timestamp, details_of_assessment=DetailsOfAssessment)
                                    newAssessment.save()
                                else:
                                    A.update(option_text = val[i])
                for warning in WarningLogQ:
                    message = message + warning + '\n'
                if message != "":
                    return HttpResponse(' Warning: \n'+message)
                else:
                    return HttpResponse("success")
            return HttpResponse("warning")
        except Exception, e:
            with open(msg_location,'w') as myfile:
                writer = csv.writer(myfile)
                if len(data) > 0:
                    writer.writerow(["Error Log for Assessments"])
                    message = message+"\n Error Log for Assessments: \n"
                    for i in range(len(data)):
                        #print(data[i])
                        writer.writerow(data[i])
                        tmp = ' '.join(str(x) for x in data[i])
                        message = message+tmp+'\n'
                if len(ErrorLogA) > 0:
                    writer.writerow(["Error Log for Assessments"])
                    message = message+"\n Error Log for Assessments: \n"
                    for i in range(len(ErrorLogA)):
                        writer.writerow([ErrorLogA[i]])
                        tmp = ' '.join(str(x) for x in ErrorLogA[i])
                        message = message+tmp+'\n'
                if len(ErrorLogQ) > 0:
                    writer.writerow(["ErrorLog Log for Questions"])
                    message = message+"\n Error Log for Questions: \n"
                    for i in range(len(ErrorLogQ)):
                        writer.writerow([ErrorLogQ[i]])
                        tmp = ' '.join(str(x) for x in ErrorLogQ[i])
                        message = message+tmp+'\n'
                myfile.flush()
                print message
                return HttpResponse("error"+'\n'+message+'\n'+str(e))
    ##############################################ENDING CODE###########################################
    return render(request, "ucs/batch_import.html",{"message": message, "username": request.session.get("username")})


def scoring(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    message = None

    question_set = Question.objects.all()
    cata_set = Category.objects.all()
    user_set = User.objects.all()
    group_set = Group.objects.all()

    current_user = User.objects.get(id= user_id)
    print current_user
    #####################JASON######################
    if current_user.admin_user == True:
        assignment_set = Assignment.objects.all()
    else:
        try:
            assignment_set = []
            #Regular User
            user_work = Assignment_log.objects.filter(user_id = user_id)
            #Loop through user assignments
            for uw in user_work:
                if uw.finish_date != "0000-00-00":
                    assignment_set.append(uw.assignment_id)
            #print 'Existing Assignments:', assignment_set
        except Exception, e:
            print e
    #####################JASON######################
    question_list = []
    cata_list = []
    user_list = []
    group_list = []
    assignment_list = []
    for qn in question_set:
        question_list.append(qn.question_text)
    for cn in cata_set:
        cata_list.append(cn.category_text)
    for un in user_set:
        user_list.append(un.username)
    for gn in group_set:
        group_list.append(gn.group_name)
    for an in assignment_set:
        assignment_list.append(an.assignment_name)
    question_data = [{"question":q} for q in question_list]
    cata_data = [{"category":c} for c in cata_list]
    user_data = [{"user":u} for u in user_list]
    group_data = [{"group":g} for g in group_list]
    assignment_data = [{"assignment":a} for a in assignment_list]
    #print question_data
    #print cata_data
    #print user_data
    #print group_data
    #print assignment_data
    json_question = json.dumps(question_data)
    json_cata = json.dumps(cata_data)
    if current_user.admin_user==True:
        json_user = json.dumps(user_data)
        json_group = json.dumps(group_data)
    else:
        json_user = json.dumps([])
        json_group = json.dumps([])
    json_assignment = json.dumps(assignment_data)
    if request.method == "POST":
            data['rep_message'] = 'Success'
            data['status'] = True
            return JsonResponse(data)
    return render(request, "ucs/scoring.html",{"message": message, "username": request.session.get("username"), "questionList": json_question,
        "cataList": json_cata, "userList": json_user, "groupList": json_group, "assignmentList": json_assignment})


def plotting(request):
    return render(request, "ucs/plotting.html", {})


def result(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    current_user = User.objects.get(id= user_id)
    summary_results = {}
    plot = []
    summary_results['confidence']  = "Not Calculated"
    summary_results['calibration'] = "Not Calculated"
    summary_results['resolution']  = "Not Calculated"
    summary_results['knowledge']   = "Not Calculated"
    summary_results['brierscore']  = "Not Calculated"

    datapoints = []
    if request.method == "POST":
        #Process request to get answer containing all option selected on scoring page
        answer = processRequests(request,current_user)
        print "answer\n\n\n\n", answer
        #answer = [question_type, forecast, question_purpose, question_text, true_or_false, category, user_name, group_name, assignment_name, date_submitted]

        #write answer in the file
        if 'Windows' in platform.system():
            if not os.path.isdir('tmp/'):
                os.makedirs('tmp/')

        #Log File
        with open(log_path, 'wb') as csvfile:
            para_fieldnames = ['Question Type', 'Forecast', 'Question Purpose', 'Question Text', '# of Choices', 'Category', 'User', 'Group', 'Assignment Name', 'Date Submitted']
            writer = csv.DictWriter(csvfile, fieldnames=para_fieldnames)
            writer.writeheader()
            writer.writerow({'Question Type': answer[0], 'Forecast': answer[1], 'Question Purpose': answer[2], 'Question Text': answer[3], '# of Choices': answer[4], 'Category': answer[5], 'User': answer[6], 'Group': answer[7], 'Assignment Name': answer[8], 'Date Submitted': answer[9]})
            csvfile.write("\n\n\n");

        ##################IT'S NO LONGER RAUL CODE######################
        QSet, ASet = returnAssessments(answer, 0, "", "")
        QA_map = {} #Mapping of questions to assessments
        temp = ASet.values()
        with open(log_path, 'a') as csvfile:
            assessment_fieldnames = ['Question ID', 'Date of assessment','User Name','Operator','Answer Text','Details Of Assessment','Option Text','ID']
            writer = csv.DictWriter(csvfile, fieldnames=assessment_fieldnames,lineterminator='\n')
            writer.writeheader()
            for value in temp:
                print "value: ", value
                writer.writerow({'Question ID':value['question_id_id'], 'Date of assessment':value['date_of_assessment'],
             'User Name':User.objects.get(pk=value['user_id_id']).username, 'Operator':value['operator'],'Answer Text':value['answer_text'],
             'Details Of Assessment':value['details_of_assessment'], 'Option Text':value['option_text'],'ID':value['id']})
                if value['question_id_id'] not in QA_map.keys():
                    QA_map[value['question_id_id']] = {}
                else:
                    pass
                AKey = str(value['user_id_id'])+'_'+value['date_of_assessment']+'_'+value['time_of_assessment']
                if AKey not in QA_map[value['question_id_id']].keys():
                    QA_map[value['question_id_id']][AKey] = []
                else:
                    pass
                QA_map[value['question_id_id']][AKey].append(value)
            csvfile.write("\n\n\n");


        summary_results, values, plot, datapoints = computeResults(ASet)
        summary_fieldnames = ['Confidence', 'Calibration', 'Resolution', 'Knowledge', 'Brierscore']
        insert_data_to_debug_file_vertically(summary_fieldnames,values,'a')

        #Get WLS line, confidence bias, and directional bias
        wls_datapoints, wls_c_d_table = wls_bias_calc(plot)
        ################################################################

        A_len_list = [len(QA_map[i][j]) for i in QA_map for j in QA_map[i]]
        if not A_len_list:
            max_assessment_size = 0
        else:
            max_assessment_size = max(A_len_list)

        with open(data_path, 'wb') as csvfile:
            data_fieldnames = ['USER', 'ASSIGNMENT', 'TRAINING', 'FORECAST', 'DISCRETE', 'NO OF CHOICES', 'CATEGORY', 'QUESTION TEXT', 'DATE TRUE VALUE KNOWN', 'TRUE VALUE', 'UNITS', 'ANSWER SOURCE', 'ALLOW ASSESSMENT', 'DATE OF ASSESSMENT', 'OPERATOR', 'ASSESSMENT DETAILS', 'NUMBER OF PAIRS']
            for i in range(max_assessment_size):
                data_fieldnames.append('PROB '+str(i+1))
                data_fieldnames.append('VALUE '+str(i+1))
            writer = csv.DictWriter(csvfile, fieldnames=data_fieldnames)
            writer.writeheader()

            for qn in QSet:
                if qn.id not in QA_map.keys():
                    pass
                else:
                    for AKey in QA_map[qn.id]:
                        #Data File
                        data = {}
                        #data['QUESTIONID'] = qn.id
                        data['QUESTION TEXT'] = qn.question_text.encode('utf-8')
                        data['ASSIGNMENT'] = ""
                        data['TRAINING'] = str(qn.corporate_training)
                        data['FORECAST'] = str(qn.forecast)
                        data['DISCRETE'] = str(qn.question_type)
                        data['NO OF CHOICES'] = qn.num_of_choices
                        data['CATEGORY'] = str(qn.category).encode('utf-8')
                        data['DATE TRUE VALUE KNOWN'] = str(qn.upload_date)
                        data['TRUE VALUE'] = qn.true_value
                        data['UNITS'] = str(qn.unit).encode('utf-8')
                        data['ANSWER SOURCE'] = str(qn.question_source).encode('utf-8')
                        data['ALLOW ASSESSMENT'] = str(qn.allow_assessment)
                        if len(QA_map[qn.id][AKey]) == 0:
                            data['USER'] = ''
                            data['DATE OF ASSESSMENT'] = '0000-00-00'
                            data['OPERATOR'] = 'EQ'
                            data['ASSESSMENT DETAILS'] = ''
                        else:
                            assessor = User.objects.get(id= QA_map[qn.id][AKey][0]['user_id_id'])
                            data['USER'] = assessor
                            data['DATE OF ASSESSMENT'] = str(QA_map[qn.id][AKey][0]['date_of_assessment'])
                            data['OPERATOR'] = str(QA_map[qn.id][AKey][0]['operator'])
                            data['ASSESSMENT DETAILS'] = str(QA_map[qn.id][AKey][0]['details_of_assessment']).encode('utf-8')
                        data['NUMBER OF PAIRS'] = len(QA_map[qn.id][AKey])
                        for j in range(data['NUMBER OF PAIRS']):
                            ###JASON 06-17###
                            a_set = Assignment.objects.get(id = QA_map[qn.id][AKey][j]['assignment_id_id'])
                            data['ASSIGNMENT'] = a_set.assignment_name
                            data['PROB '+str(j+1)]  = QA_map[qn.id][AKey][j]['answer_text']
                            data['VALUE '+str(j+1)] = QA_map[qn.id][AKey][j]['option_text']
                        writer.writerow(data)
            csvfile.write("\n\n\n");
    return render(request, "ucs/result.html", {"summary":json.dumps(summary_results),"datapoints":datapoints,"plot":plot, "wls_datapoints": wls_datapoints, "wcd_table": wls_c_d_table})


def result_test(request):
    
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    current_user = User.objects.get(id= user_id)
    summary_results = {}
    plot = []
    summary_results['confidence']  = "Not Calculated"
    summary_results['calibration'] = "Not Calculated"
    summary_results['resolution']  = "Not Calculated"
    summary_results['knowledge']   = "Not Calculated"
    summary_results['brierscore']  = "Not Calculated"

    datapoints = []
    if request.method == "POST":
        #Process request to get answer containing all option selected on scoring page
        answer = processRequests(request,current_user)
        #print "answer\n\n\n\n", answer
        #answer = [question_type, forecast, question_purpose, question_text, true_or_false, category, user_name, group_name, assignment_name, date_submitted]

        #write answer in the file
        #if not os.path.isdir('debug\\'):
        #    os.makedirs('debug\\')
        #Log File
        sumresult_list = {}
        values_list = []
        plot_list = []
        datapoints_list = {}
        wls_dp_list = []
        wls_c_d_list = {}
        if answer[14] == 1:
            with open(log_path, 'wb') as csvfile:
                para_fieldnames = ['Question Type', 'Forecast', 'Question Purpose', 'Question Text', '# of Choices', 'Category', 'User', 'Group', 'Assignment Name', 'Date Submitted']
                writer = csv.DictWriter(csvfile, fieldnames=para_fieldnames)
                writer.writeheader()
                writer.writerow({'Question Type': answer[0], 'Forecast': answer[1], 'Question Purpose': answer[2], 'Question Text': answer[3], '# of Choices': answer[4], 'Category': answer[5], 'User': answer[6], 'Group': answer[7], 'Assignment Name': answer[8], 'Date Submitted': answer[9]})
                csvfile.write("\n\n\n");
            ##################IT'S NO LONGER RAUL CODE######################
            QSet, ASet = returnAssessments(answer, 0, "", "")
            QA_map = {} #Mapping of questions to assessments
            temp = ASet.values()
            with open(log_path, 'a') as csvfile:
                assessment_fieldnames = ['Question ID', 'Date of assessment','User Name','Operator','Answer Text','Details Of Assessment','Option Text','ID']
                writer = csv.DictWriter(csvfile, fieldnames=assessment_fieldnames,lineterminator='\n')
                writer.writeheader()
                for value in temp:
                    #print "value: ", value
                    writer.writerow({'Question ID':value['question_id_id'], 'Date of assessment':value['date_of_assessment'],
                 'User Name':User.objects.get(pk=value['user_id_id']).username, 'Operator':value['operator'],'Answer Text':value['answer_text'],
                 'Details Of Assessment':value['details_of_assessment'], 'Option Text':value['option_text'],'ID':value['id']})
                    if value['question_id_id'] not in QA_map.keys():
                        QA_map[value['question_id_id']] = []
                    else:
                        pass
                    '''AKey = str(value['user_id_id'])+'_'+value['date_of_assessment']+'_'+value['time_of_assessment']
                    if AKey not in QA_map[value['question_id_id']].keys():
                        QA_map[value['question_id_id']][AKey] = []
                    else:
                        pass'''
                    QA_map[value['question_id_id']].append(value)
                csvfile.write("\n\n\n");
            summary_results, values, plot, datapoints = computeResults(ASet)
                
            summary_fieldnames = ['Confidence', 'Calibration', 'Resolution', 'Knowledge', 'Brierscore']
            insert_data_to_debug_file_vertically(summary_fieldnames,values,'a')

            #Get WLS line, confidence bias, and directional bias
            wls_datapoints, wls_c_d_table = wls_bias_calc(plot)
            ## Split into loop field sets
            if answer[11] is not None:
                answer_copy     = answer
                get_assessments = ASet.values()
                loop_set        = {}
                for val in get_assessments:
                    usr = User.objects.get(pk=val['user_id_id']).username
                    if usr not in loop_set:
                        loop_set[usr] = []
                    loop_set[usr].append(val)
                for key in loop_set:
                    answer_copy[6] = key
                    UserID = User.objects.get(username=key)
                    temp_QSet, temp_ASet = returnAssessments(answer_copy, 1, UserID, "user")
                    srt, vt, pt, dpt     = computeResults(temp_ASet)
                    print "srt: ", len(srt)
                    print "vt: ", len(vt)
                    print "pt: ", len(pt)
                    print "dpt: ", len(dpt)
                    sumresult_list[key]  = srt
                    values_list.append(vt)
                    plot_list.append(pt)
                    datapoints_list[key] = dpt
                    wdt, wcdt = wls_bias_calc(pt)
                    wls_dp_list.append(wdt)
                    wls_c_d_list[key] = wcdt
                wls_c_d_list = json.dumps(wls_c_d_list)
                sumresult_list = json.dumps(sumresult_list)
                datapoints_list = json.dumps(datapoints_list)
                option = json.dumps("User");
                return render(request, "ucs/result_test.html", {"loop_option": option, "wcd_table_org": wls_c_d_table, "summary_org": summary_results, "summary":sumresult_list,"datapoints":datapoints,"plot":plot, "wls_datapoints": wls_datapoints, "wcd_table": wls_c_d_list, "dp_list": datapoints_list})
            elif answer[12] is not None:
                answer_copy = answer
                get_assessments = ASet.values()
                loop_set = {}
                group_id_pos = 0
                get_grps = Assigned_group.objects.all()
                for val in get_grps:
                    if val.group_id not in loop_set:
                        loop_set[val.group_id.group_name] = []
                for key in loop_set:
                    answer_copy[7] = key
                    GroupID = Group.objects.get(group_name=key)
                    temp_QSet, temp_ASet = returnAssessments(answer_copy, 1, GroupID, "group")
                    print "JJ: ", len(temp_QSet), len(temp_ASet)
                    srt, vt, pt, dpt = computeResults(temp_ASet)
                    sumresult_list[key] = srt
                    values_list.append(vt)
                    plot_list.append(pt)
                    datapoints_list[key] = dpt
                    wdt, wcdt = wls_bias_calc(pt)
                    wls_dp_list.append(wdt)
                    wls_c_d_list[key] = wcdt
                    group_id_pos = group_id_pos + 1
                wls_c_d_list = json.dumps(wls_c_d_list)
                sumresult_list = json.dumps(sumresult_list)
                datapoints_list = json.dumps(datapoints_list)
                option = json.dumps("Group");
                return render(request, "ucs/result_test.html", {"loop_option": option, "wcd_table_org": wls_c_d_table, "summary_org": summary_results,"summary":sumresult_list,"datapoints":datapoints,"plot":plot, "wls_datapoints": wls_datapoints, "wcd_table": wls_c_d_list, "dp_list": datapoints_list})
            elif answer[13] is not None:
                if not answer[16] or not answer[17] or not answer[18]:
                    pass
                else:
                    start_time = datetime.strptime(date_norm(answer[17]), "%Y-%m-%d").date()
                    end_time = datetime.strptime(date_norm(answer[16]), "%Y-%m-%d").date()
                    time_filter_list = []
                    time_factor = int(answer[18]) #Bin spaceing               
                    if answer[15] == "Day":
                        time_cond = start_time
                        while time_cond <= end_time :
                            time_filter_list.append(time_cond.strftime("%Y-%m-%d"))
                            time_cond = time_cond + timedelta(days=time_factor)
                    elif answer[15] == "Week":
                        time_cond = start_time
                        time_factor = time_factor * 7
                        while time_cond <= end_time :
                            time_filter_list.append(time_cond.strftime("%Y-%m-%d"))
                            time_cond = time_cond + timedelta(days=time_factor)            
                    elif answer[15] == "Month":
                        time_cond = start_time
                        time_factor = time_factor * 30
                        while time_cond <= end_time :
                            time_filter_list.append(time_cond.strftime("%Y-%m-%d"))
                            time_cond = time_cond + timedelta(days=time_factor)       
                    elif answer[15] == "Year":
                        time_cond = start_time
                        time_factor = time_factor * 364
                        while time_cond <= end_time :
                            time_filter_list.append(time_cond.strftime("%Y-%m-%d"))
                            time_cond = time_cond + timedelta(days=time_factor)
                    for key in time_filter_list:
                        time_list = []
                        prev_time = datetime.strptime(key, "%Y-%m-%d").date()
                        prev_time = prev_time - timedelta(days=time_factor)
                        curr_time = datetime.strptime(key, "%Y-%m-%d").date()
                        while prev_time <= curr_time :
                            time_list.append(prev_time.strftime("%Y-%m-%d"))
                            prev_time = prev_time + timedelta(days=1)
                        temp_QSet, temp_ASet = returnAssessments(answer, 1, time_list, "time")
                        print "JJ: ", len(temp_QSet), len(temp_ASet)
                        srt, vt, pt, dpt = computeResults(temp_ASet)
                        sumresult_list[key] = srt
                        values_list.append(vt)
                        plot_list.append(pt)
                        datapoints_list[key] = dpt
                        wdt, wcdt = wls_bias_calc(pt)
                        wls_dp_list.append(wdt)
                        wls_c_d_list[key] = wcdt
                    wls_c_d_list = json.dumps(wls_c_d_list)
                    sumresult_list = json.dumps(sumresult_list)
                    datapoints_list = json.dumps(datapoints_list)
                    option = json.dumps("Time");
                    return render(request, "ucs/result_test.html", {"loop_option": option, "wcd_table_org": wls_c_d_table, "summary_org": summary_results,"summary":sumresult_list,"datapoints":datapoints,"plot":plot, "wls_datapoints": wls_datapoints, "wcd_table": wls_c_d_list, "dp_list": datapoints_list})
            usr_key = User.objects.get(pk=user_id).username
            sumresult_list[usr_key] = summary_results
            wls_c_d_list[usr_key] = wls_c_d_table
            sumresult_list = json.dumps(sumresult_list)
            wls_c_d_list = json.dumps(wls_c_d_list)
            ################################################################
            return render(request, "ucs/result_test.html", {"summary":sumresult_list,"datapoints":datapoints,"plot":plot, "wls_datapoints": wls_datapoints, "wcd_table": wls_c_d_list})

def wls_bias_calc(plot):
    sum_x = 0
    sum_y = 0
    sum_w = 0
    X_bar = 0
    Y_bar = 0
    BETA_1 = 0
    BETA_0 = 0
    denom = 0
    for row in plot:
        sum_x += row[0]
        sum_y += row[1]
        sum_w += row[2]
        X_bar += row[2]*row[0]
        Y_bar += row[2]*row[1]
    if sum_w == 0:
        sum_w = 0.01
    X_bar = X_bar / sum_w
    Y_bar = Y_bar / sum_w

    for row in plot:
        BETA_1 += row[2]*(row[0]-X_bar)*(row[1]-Y_bar)
        denom += row[2]*(math.pow((row[0]-X_bar),2))
    if denom == 0:
        denom = 0.01
    BETA_1 = BETA_1 / denom
    BETA_0 = Y_bar - BETA_1*X_bar
    if BETA_1 == 0:
        BETA_1 = 0.01
    #BETA_1 is WLS slope
    #BETA_0 is WLS intercept
    wls_datapoints = []
    CB = 0 #Confident bias
    DB = 0 #Directional bias
    xy_points = 0
    for i in range(11):
        x = xy_points
        y = xy_points
        temp = {}
        temp['y'] = BETA_1*x+BETA_0
        temp['x'] = (temp['y']-BETA_0)/BETA_1
        wls_datapoints.append(temp)
        xy_points += 0.1
    if BETA_1 > 1:
        CB = (1/BETA_1) - 1
        DB = 1 - (2*BETA_0)/(1-BETA_1)
    elif BETA_1 < 1:
        CB = 1- BETA_1
        DB = (2*BETA_0)/(1-BETA_1)-1
    wls_c_d_table_data = {"cbias":round(CB,3), "dbias":round(DB,3), "slope": round(BETA_1,3), "intercept": round(BETA_0,3)}
    #wls_c_d_table = json.dumps(wls_c_d_table_data)

    return wls_datapoints, wls_c_d_table_data
    

def download_log(request):
    #zip("debug\\","debugzip")
    #file_path = "debugzip.zip"
    if os.path.exists(log_path):
        with open(log_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(log_path)
            return response
    else:
        return HttpResponse("<h1>File not found.</h1>")


def batch_export(request):
    if os.path.exists(data_path):
        with open(data_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(data_path)
            return response
    else:
        return HttpResponse("<h1>File not found.</h1>")


## Function to insert data into debug.csv
def insert_data_to_debug_file_vertically(fieldnames,values,file_mode):
    with open(log_path, file_mode) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Parameter','Value'],lineterminator='\n')
        writer.writeheader()
        for key in fieldnames:
            writer.writerow({'Parameter':key,'Value':values[key]})


def processRequests(req,current_user):
    ###########################################
    question_type = req.POST.get("question_type")
    if question_type == '1':
        '''A Discrete Question'''
        question_type = True
    elif question_type == '0':
        question_type = False
    else:
        question_type = None
    ###########################################
    forecast = req.POST.get("forecast")
    if forecast == '1':
        '''A Forecast Question'''
        forecast = True
    elif forecast == '0':
        forecast = False
    else:
        forecast = None
    ###########################################
    question_use = req.POST.get("question_use")
    if question_use == '1':
        '''A Training Question'''
        question_use = True
    elif question_use == '0':
        question_use = False
    else:
        question_use = None
    ###########################################
    question_text = req.POST.get("question_text")
    ###########################################
    true_or_false = req.POST.get("number_of_choice")
    if true_or_false:
        true_or_false = int(true_or_false)
    ###########################################
    category = req.POST.get("category")

    if current_user.admin_user==True:
        user_name = req.POST.get("user")
    else:
        user_name = current_user.username

    group_name = req.POST.get("group")
    assignment_name = req.POST.get("assignment_name")
    #DJ-Check for Looping call - T for true
    loop_check = req.POST.get("loop_call")
    # edate means ending date and sdate means start date
    # [sdate, edate] closed interval
    if loop_check == "T":
        edate_submitted = req.POST.get("sub_edate")
        sdate_submitted = req.POST.get("sub_sdate")
        # Assignment Finish Dates
        edate_f_assign = req.POST.get("f_edate")
        sdate_f_assign= req.POST.get("f_sdate")  
        # Question close date
        edate_c_question = req.POST.get("q_edate")
        sdate_c_question= req.POST.get("q_sdate") 
        # loop option
        user_loop = req.POST.get("userloop")
        group_loop = req.POST.get("grouploop")
        
        timeloop = req.POST.get("timeloop");
        bin_type = "None"
        if req.POST.get("binday") == "on":
            bin_type = "Day"
        elif req.POST.get("binweek") == "on":
            bin_type = "Week"
        elif req.POST.get("binmonth") == "on":
            bin_type = "Month"
        elif req.POST.get("binyear") == "on":
            bin_type = "Year"
        timeloop_edate = req.POST.get("timeloop_edate");
        timeloop_sdate = req.POST.get("timeloop_sdate");
        binscale = req.POST.get("binscale")
        
        loop_request = 1;           
        print "LOOP CHECK"
        answer = [question_type, forecast, question_use, question_text, true_or_false, category, user_name, group_name, assignment_name, edate_submitted
        , sdate_submitted, user_loop, group_loop, timeloop, loop_request, bin_type, timeloop_edate, timeloop_sdate, binscale]
        return answer
    #print req.POS.get("date_submitted")
    answer = [question_type, forecast, question_use, question_text, true_or_false, category, user_name, group_name, assignment_name, req.POST.get("date_submitted")]
    #print "answer \n\n",answer
    return answer


def returnAssessments(answer, check, loop_filter, loop_type):
    if check == 0:
        QSet = Question.objects.all()
        #print "Question Object: ", QSet.all()
        if answer[8]:
            Q_text = []
            A_id = Assignment.objects.get(assignment_name=answer[8])
            ASet = Assessment.objects.filter(assignment_id=A_id)
            ##AQ_objs = Assigned_question.objects.filter(assignment_id=A_id)
            ##for obj in AQ_objs:
            ##    Q_text.append(obj.question_id)
            ##print 'QText: ', QText
            ##QSet = Question.objects.filter(question_text__in=Q_text)
            #print 'QSet: ', QSet
            #print answer[8]
        else:
            ASet = Assessment.objects.filter(question_id__in=QSet)
            print 'The assignment name is not specified'
            print "Number of Assessment: ", len(ASet)
        if answer[0] is not None:
            QSet = Question.objects.filter(id__in=QSet, question_type=answer[0])
            #print 'GOT VALUE'
        else:
            print 'The question type is not specified'
        if answer[1] is not None:
            QSet = Question.objects.filter(id__in=QSet, forecast=answer[1])
            #print 'GOT VALUE'
        else:
            print 'The forecast permission is not specified'
        if answer[2] is not None:
            QSet = Question.objects.filter(id__in=QSet, corporate_training=answer[2])
            #print 'GOT VALUE'
        else:
            print 'The coporate training is not specified'
        if answer[3]:
            QSet = Question.objects.filter(id__in=QSet, question_text=answer[3])
            #print 'GOT VALUE'
        else:
            print 'The question text is not specified'
        if answer[4]:
            QSet = Question.objects.filter(id__in=QSet, num_of_choices=answer[4])
            #print 'GOT VALUE'
        else:
            print 'The number of choices is not specified'
        if answer[5]:
            tmp  = Category.objects.get(category_text=answer[5])
            QSet = Question.objects.filter(id__in=QSet, category=tmp)
            #print 'GOT VALUE'
            #print tmp
        else:
            print 'The category is not specified'
        #Query on question_set, user_name, and ...

        ASet = Assessment.objects.filter(id__in=ASet, question_id__in=QSet)

        if answer[7]:
            G_user = []
            G_id = Group.objects.get(group_name=answer[7])
            GM_objs = Group_member.objects.filter(group_id=G_id)
            for obj in GM_objs:
                G_user.append(obj.user_id)
            ASet = Assessment.objects.filter(id__in=ASet, user_id__in=G_user)
        else:
            print 'The group is not specified'
        if answer[6]:
            upload_user = User.objects.get(username=answer[6])#no need to change
            #print "User Object: ", upload_user
            ASet = Assessment.objects.filter(id__in=ASet, user_id=upload_user)
            #print len(ASet)
            #print "username ",answer[6]
        else:
            print 'The user name is not specified'
        if answer[9] and answer[10]:
      
                start_time = datetime.strptime(date_norm(answer[10]), "%Y-%m-%d").date()
                end_time = datetime.strptime(date_norm(answer[9]), "%Y-%m-%d").date()
                time_filter_list = []
                time_cond = start_time
                print "START_TIME", start_time
                print "END_TIME", end_time
                while time_cond <= end_time :
                    time_filter_list.append(time_cond.strftime("%Y-%m-%d"))
                    time_cond = time_cond + timedelta(days=1)
                print "Aset 1", ASet       

                ASet = Assessment.objects.filter(id__in=ASet, date_of_assessment__in=time_filter_list)

                print "Aset 2, ", ASet
        else:
            print 'The date of assessment is not specified'

    elif check == 2:
        #DJ's code for the looping
        ''' 
        answer = [question_type, forecast, question_use, question_text, true_or_false, category, user_name, group_name, assignment_name, edate_submitted
        sdate_submitted, edate_f_assign, sdate_f_assign, edate_c_question, sdate_c_question, loop_request]
        answer[9-10] := assessment Date submitted
        answer[11-12] := assignment finish date
        answer[13-14] := question upload date
        answer[15] := loop_request
        '''
        #"""
        target_assignments = []
        question_set = []
        if loop_type == "user":
            get_assign_list = Assignment_log.objects.filter(finish_date__gt="0000-00-00", user_id=loop_filter)
        elif loop_type == "group":
            get_assign_list = Assignment_log.objects.filter(finish_date__gt="0000-00-00", group_id=loop_filter)
        elif loop_type == "time":
            get_assign_list = Assignment_log.objects.filter(finish_date__in=loop_filter)

        print "get_assign_list: ", get_assign_list
        for asn in get_assign_list:
            if answer[8]:
                if asn.assignment_id.assignment_name == answer[8]:
                    target_assignments.append(asn.assignment_id)
            else:
                target_assignments.append(asn.assignment_id)
        qs_list = Assigned_question.objects.filter(assignment_id__in=target_assignments)
        for ql in qs_list:
            ql = Question.objects.filter(question_text=ql.question_id.question_text)
            for q in ql:
                question_set.append(q)
        if answer[0] is not None:
            question_set = [qs for qs in question_set if qs.question_type == answer[0]]
        if answer[1] is not None:
            question_set = [qs for qs in question_set if qs.forecast == answer[1]]
        if answer[2] is not None:
            question_set = [qs for qs in question_set if qs.corporate_training == answer[2]]
        if answer[3]:  
            question_set = [qs for qs in question_set if qs.question_text == answer[3]]
        if answer[4]:
            question_set = [qs for qs in question_set if qs.num_of_choices == answer[4]]
        if answer[5]:
            cond_val = Category.objects.get(category_text=answer[5])
            question_set = [qs for qs in question_set if qs.category == cond_val]
        #print question_set
        a_set = []
        '''if answer[9] != "" and answer[10] != "":
            get_assessments = Assessment.objects.filter(question_id__in=question_set, date_of_assessment__range=[answer[10], answer[9]])
        elif answer[9] == "" and answer[10] != "":
            get_assessments = Assessment.objects.filter(question_id__in=question_set, date_of_assessment__range=[answer[10], "2100-01-01"])
        elif answer[10] ==  "" and answer[9] != "":
            get_assessments = Assessment.objects.filter(question_id__in=question_set, date_of_assessment__range=["0000-00-00", answer[9]])
'''
        if answer[9] and answer[10]:
  
            start_time = datetime.strptime(date_norm(answer[10]), "%Y-%m-%d").date()
            end_time = datetime.strptime(date_norm(answer[9]), "%Y-%m-%d").date()
            time_filter_list = []
            time_cond = start_time
            while time_cond <= end_time :
                time_filter_list.append(time_cond.strftime("%Y-%m-%d"))
                time_cond = time_cond + timedelta(days=1)    
            get_assessments = Assessment.objects.filter(id__in=ASet, date_of_assessment__in=time_filter_list)
        else:
            get_assessments = Assessment.objects.filter(question_id__in=question_set)
        #startDate = answer[10].split("/")
        #endDate   = answer[9].split("/")
        
        #get_assessments = Assessment.objects.filter(question_id__in=question_set)
        for ga in get_assessments:
            a_set.append(ga)
            #print ga.date_of_assessment
        if answer[6]:
            user = User.objects.get(username = answer[6])
            a_set = [a for a in a_set if a.user_id == user]
        if answer[7]:
            G_user = []
            G_id = Group.objects.get(group_name=answer[7])
            GM_objs = Group_member.objects.filter(group_id=G_id)
            for obj in GM_objs:
                G_user.append(obj.user_id)
            a_set = [a for a in a_set if a.user_id in G_user]
        a_set_qid = []
        for a in a_set:
            a_set_qid.append(a.question_id)
        #print a_set
        QSet = Question.objects.filter(question_text__in=question_set)
        ASet = Assessment.objects.filter(question_id__in=a_set_qid)
        print "#######################################################"
        print QSet
        print ASet
        print "#######################################################"
        #"""
    else:
        
        ''' 
        answer = [question_type, forecast, question_use, question_text, true_or_false, category, user_name, group_name, assignment_name, edate_submitted
        sdate_submitted, edate_f_assign, sdate_f_assign, edate_c_question, sdate_c_question, loop_request]
        answer[9-10] := assessment Date submitted
        answer[11-12] := assignment finish date
        answer[13-14] := question upload date
        answer[15] := loop_request
        '''
        target_assignments = []
        if loop_type == "user":
            get_assign_list = Assignment_log.objects.filter(finish_date__gt="0000-00-00", user_id=loop_filter)
            #get_assign_list = Assessment.objects.filter(user_id=loop_filter)
        elif loop_type == "group":
            get_assign_list = Assignment_log.objects.filter(finish_date__gt="0000-00-00", group_id=loop_filter)
        elif loop_type == "time":
            get_assign_list = Assignment_log.objects.filter(finish_date__in=loop_filter)
        
        print "get_assign_list: ", get_assign_list
        for asn in get_assign_list:
            if answer[8]:
                if asn.assignment_id.assignment_name == answer[8]:
                    target_assignments.append(asn.assignment_id)
            else:
                target_assignments.append(asn.assignment_id)
        ################################################################################
        print "target_assignments: ", len(target_assignments)
        ASet = Assessment.objects.filter(assignment_id__in=target_assignments)

        
        """
        qs_list = Assigned_question.objects.filter(assignment_id__in=target_assignments)
        for ql in qs_list:
            ql = Question.objects.filter(question_text=ql.question_id.question_text)
            for q in ql:
                question_set.append(q)
        """
        print "ASet: >>>> ", ASet

        ################################################################################
        QSet = Question.objects.all()
        if answer[0] is not None:
            QSet = [qs for qs in QSet if qs.question_type == answer[0]]
        if answer[1] is not None:
            QSet = [qs for qs in QSet if qs.forecast == answer[1]]
        if answer[2] is not None:
            QSet = [qs for qs in QSet if qs.corporate_training == answer[2]]
        if answer[3]:  
            QSet = [qs for qs in QSet if qs.question_text == answer[3]]
        if answer[4]:
            QSet = [qs for qs in QSet if qs.num_of_choices == answer[4]]
        if answer[5]:
            cond_val = Category.objects.get(category_text=answer[5])
            QSet = [qs for qs in QSet if qs.category == cond_val]
        print "QSet ASet: ", len(QSet), len(ASet)
        #print question_set
        ###a_set = []
        #print "A9: ", answer[9]
        #print "A10: ", answer[10]
#        if answer[9] != "" and answer[10] != "":
#            ASet = Assessment.objects.filter(id__in=ASet, question_id__in=QSet, date_of_assessment__range=[answer[10], answer[9]])
#        elif answer[9] == "" and answer[10] != "":
#            ASet = Assessment.objects.filter(id__in=ASet, question_id__in=QSet, date_of_assessment__range=[answer[10], "2100-01-01"])
#        elif answer[10] ==  "" and answer[9] != "":
#            ASet = Assessment.objects.filter(id__in=ASet, question_id__in=QSet, date_of_assessment__range=["0000-00-00", answer[9]])
        if answer[10] and answer[9]:
            start_time = datetime.strptime(date_norm(answer[10]), "%Y-%m-%d").date()
            end_time = datetime.strptime(date_norm(answer[9]), "%Y-%m-%d").date()
            time_filter_list = []
            time_cond = start_time
            while time_cond <= end_time :
                time_filter_list.append(time_cond.strftime("%Y-%m-%d"))
                time_cond = time_cond + timedelta(days=1)    
            ASet = Assessment.objects.filter(id__in=ASet, date_of_assessment__in=time_filter_list)

        else:
            ASet = Assessment.objects.filter(id__in=ASet, question_id__in=QSet)
            #print "HERERE", ASet
        #startDate = answer[10].split("/")
        #endDate   = answer[9].split("/")
        
        #get_assessments = Assessment.objects.filter(question_id__in=question_set)
        ##for ga in get_assessments:
        ##    a_set.append(ga)
        ##    #print ga.date_of_assessment
        
        print "QSet ASet: ", len(QSet), len(ASet)
        if answer[6]:
            print "A6...", loop_filter
            upload_user = User.objects.get(username = answer[6])
            ASet = [a for a in ASet if a.user_id == upload_user]
        if answer[7]:
            print "A7...", loop_filter
            #print "A7...LEN", len(loop_filter)
            if loop_filter.group_name == "No Users":
                G_user = User.objects.all()
                print "G_user: ", G_user
                ASet = [a for a in ASet if a.user_id in G_user]               
            else:
                G_user = []
                G_id = Group.objects.get(group_name=answer[7])
                GM_objs = Group_member.objects.filter(group_id=G_id)
                print "GM...", GM_objs
                for obj in GM_objs:
                    G_user.append(obj.user_id)
                ASet = [a for a in ASet if a.user_id in G_user]
        
        #a_set_qid = []
        #for a in a_set:
        #    a_set_qid.append(a.question_id)
        #print a_set
        ###QSet = Question.objects.filter(question_text__in=question_set)
        ###ASet = Assessment.objects.filter(question_id__in=a_set_qid)
        print "QSet ASet: ", len(QSet), len(ASet)
        print "QSet: ", QSet
        print "ASet: ***", ASet
    return (QSet, ASet)


def computeResults(ASet):
    data=[]
    intervals = 11          #change to field from form
    mindata = 5
    bins = [0 + x/float(intervals) for x in range(0,intervals+1)]
    bins[0] = -0.000001
    values = defaultdict(lambda: "Not Calculated")  ## Values of fieldnames dumped into the file
    bin_data = [] #For DEBUG
    counter = []
    summary_results = {}
    plot = []
    summary_results['confidence'] = "Not Calculated"
    summary_results['calibration'] = "Not Calculated"
    summary_results['knowledge'] ="Not Calculated"
    summary_results['resolution'] = "Not Calculated"
    summary_results['brierscore'] = "Not Calculated"
    datapoints = []
    totalcount = 0.0
    totalcorr = 0.0
    confidence = 0.0
    calibration = 0.0
    resolution = 0.0
    knowledge = 0.0

    data = processAssessments(ASet)

    #Write data to file
    with open(log_path, 'a') as csvfile:
        data_fieldnames = ['trueValue', 'operator', 'vAssigned', 'pAssigned','true_false']
        writer = csv.DictWriter(csvfile, fieldnames=data_fieldnames,lineterminator='\n')
        writer.writeheader()
        for value in data:
            writer.writerow({'trueValue': value[0], 'operator': value[1], 'vAssigned':value[2],'pAssigned':value[3],'true_false':value[4]})
        csvfile.write("\n\n\n");

    #debug_file = open("debug\debug_calculations.txt",'w')
    try:
        for j in range(len(bins)-1):
            bincorr = 0.0
            bincount = 0.0
            binprob = 0.0
            for i in range(len(data)):
                p = data[i]
                if bins[j] < p[3] and p[3] <= bins[j+1]:
                    bincount += 1
                    bincorr += p[4]
                    binprob += p[3]
            if bincount > 0:
                #DJ
                binmean = binprob/bincount
                binpercorr = bincorr/bincount
            else:
                #binmean = bins[j]
                binmean = 0.0
                binpercorr = 0.0
            if bins[j+1] <= 0.5:
                confidence = confidence + bincount*(binmean - binpercorr)
            else:
                confidence = confidence + bincount*(binpercorr - binmean)
            calibration = calibration + bincount*(binpercorr - binmean)**2
            totalcount = totalcount + bincount
            totalcorr = totalcorr + bincorr
            counter.append([bins[j+1],binpercorr,bincount])
            #PLOT DATA BASED ON MIN DATA
            if binmean > 0 or binpercorr > 0:
                plot.append([round(binmean,3),round(binpercorr,3),round(bincount,3)])
            bin_data.append([bins[j+1], bincount, bincorr, binprob, binmean, binpercorr]) #For DEBUG
        ######################Dump the bins#########################
        #Create bins Table
        with open(log_path, 'a') as csvfile:
            bin_fieldnames = ['bin', 'bincount', 'bincorr', 'binprob', 'binmean', 'binpercorr']
            writer = csv.DictWriter(csvfile, fieldnames=bin_fieldnames,lineterminator='\n')
            writer.writeheader()
            for b in bin_data:
                writer.writerow({'bin':b[0], 'bincount':b[1], 'bincorr':b[2],'binprob':b[3],'binmean':b[4], 'binpercorr':b[5]})
            csvfile.write("\n\n\n");
        ###################
        print "bins dumped to file"
        ############################################################
        for j in range(len(bins)-1):
            r = counter[j]
            print totalcount
            resolution = resolution + r[2]*(totalcorr/totalcount-r[1])**2

        # SUMMARY OF RESULTS
        confidence = confidence / totalcount
        values['Confidence'] = confidence
        calibration = calibration / totalcount
        values['Calibration'] = calibration
        resolution = resolution / totalcount
        values['Resolution'] = resolution
        knowledge = totalcorr/totalcount*(1-totalcorr/totalcount)
        values['Knowledge'] = knowledge
        brierscore = knowledge - resolution + calibration
        values['Brierscore'] = brierscore
        #print "\n\n\n\n\n\n Inside post \n\n\n\n"
        #print values

        for a in plot:
            temp = {}
            temp['x'] = round(a[0],3)
            temp['y'] = round(a[1],3)
            datapoints.append(temp)

        ###############################################################
        data1 = {}
        data1['rep_message'] = 'Success'
        data1['status'] = True

        summary_results['confidence'] = round(confidence, 3)
        summary_results['calibration'] = round(calibration, 3)
        summary_results['knowledge'] = round(knowledge, 3)
        summary_results['resolution'] = round(resolution, 3)
        summary_results['brierscore'] = round(brierscore, 3)

    except Exception as e:
            print e
            #print "Something Unexpected Happened!!!"

    return summary_results, values, plot, datapoints
    #return summary_results, values, plot, datapoints, WLS_table_json


def scoring_test(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    message = None

    question_set = Question.objects.all()
    cata_set = Category.objects.all()
    user_set = User.objects.all()
    group_set = Group.objects.all()

    current_user = User.objects.get(id= user_id)
    print current_user
    #####################JASON######################
    if current_user.admin_user == True:
        assignment_set = Assignment.objects.all()
    else:
        try:
            assignment_set = []
            #Regular User
            user_work = Assignment_log.objects.filter(user_id = user_id)
            #Loop through user assignments
            for uw in user_work:
                if uw.finish_date != "0000-00-00":
                    assignment_set.append(uw.assignment_id)
            #print 'Existing Assignments:', assignment_set
        except Exception, e:
            print e
    #####################JASON######################
    question_list = []
    cata_list = []
    user_list = []
    group_list = []
    assignment_list = []
    for qn in question_set:
        question_list.append(qn.question_text)
    for cn in cata_set:
        cata_list.append(cn.category_text)
    for un in user_set:
        user_list.append(un.username)
    for gn in group_set:
        group_list.append(gn.group_name)
    for an in assignment_set:
        assignment_list.append(an.assignment_name)
    question_data = [{"question":q} for q in question_list]
    cata_data = [{"category":c} for c in cata_list]
    user_data = [{"user":u} for u in user_list]
    group_data = [{"group":g} for g in group_list]
    assignment_data = [{"assignment":a} for a in assignment_list]
    #print question_data
    #print cata_data
    #print user_data
    #print group_data
    #print assignment_data
    json_question = json.dumps(question_data)
    json_cata = json.dumps(cata_data)
    if current_user.admin_user==True:
        json_user = json.dumps(user_data)
        json_group = json.dumps(group_data)
    else:
        json_user = json.dumps([])
        json_group = json.dumps([])
    json_assignment = json.dumps(assignment_data)
    if request.method == "POST":
            data['rep_message'] = 'Success'
            data['status'] = True
            return JsonResponse(data)
    return render(request, "ucs/scoring_test.html",{"message": message, "username": request.session.get("username"), "questionList": json_question,
        "cataList": json_cata, "userList": json_user, "groupList": json_group, "assignmentList": json_assignment})


def processAssessments(ASet):
    data = []
    for assessment in ASet:
        # QUERY FORMAT: TRUEVALUE   PASSIGNED   VASSIGNED   OPERATOR
        question = Question.objects.get(id=assessment.question_id.id)
        trueValue = question.true_value
        ### BUG HERE!! MIX OF OPTION AND ANSWER ###
        pAssigned = assessment.answer_text
        vAssigned = assessment.option_text
        ##################
        operator = assessment.operator
        #Only one dot allow in the float value
        dot_num = len(trueValue)-len(trueValue.replace('.',''))
        if dot_num <= 1 and trueValue.replace('.','').replace('-','').isdigit():
            trueValue = float(trueValue)
            pAssigned = float(pAssigned)
            vAssigned = float(vAssigned)
            # POPULATING TABLE OF OBSERVED PROBABILITIES
            if operator == "EQ":
                if trueValue == vAssigned:
                    data.append([trueValue,operator,vAssigned,pAssigned,1])
                else:
                    data.append([trueValue,operator,vAssigned,pAssigned,0])
            elif operator == "GE":
                operator = "LE"
                pAssigned = 1.0 - pAssigned
                if trueValue <= vAssigned:
                    data.append([trueValue,operator,vAssigned,pAssigned,1])
                else:
                    data.append([trueValue,operator,vAssigned,pAssigned,0])
            elif operator == "LE":
                if trueValue <= vAssigned:
                    data.append([trueValue,operator,vAssigned,pAssigned,1])
                else:
                    data.append([trueValue,operator,vAssigned,pAssigned,0])
        else:
            print assessment
    return data
