# FOR SCORING TWO LOOPS ARE NECESSARY
#import csv
#Data Reading
#path = "C:/Users/raulgonzalez88/Scoring1.csv"
#path = "C:/Users/Jason/Dropbox/Code/Apache/test/Scoring.csv"
#reader = csv.reader(open(path),delimiter=",")
#header=next(reader)

#SINGLE SCORING NO LOOPS
#BASE FILTERS
category_text = ""                          #change to field from form category.table.category
categoryObj = Category.objects.get(category_text = category_text) 

group_name = ""                             #change to field from form groups.table.name                   
groupObj = Group.objects.get(group_name = group_name)
#GET ALL THE USERS RELATED TO THAT PARTICULAR GROUP
#NEEDS TO BE DONE
#UASet = Assigned_group.objects.filter(group_id = group_name)

assignment_name = ""                        #change to field from form assignments.table.name
assignmentObj = Assignment.objects.get(assignment_name = assignment_name)
#GET ALL THE QUESTIONS RELATED TO THAT PARTICULAR ASSIGNMENT
#NEEDS TO BE DONE
#QASet = Assigned_questions.objects.filter(assignment_id = assignmentObj)

upload_user = User.objects.get(id = user_id)#no need to change 

question_use = ""                           #change to field from form questions.table.question_use
forecast = ""                               #change to field from form questions.table.forecast
question_type = ""                          #change to field from form questions.table.question_type
question_text = ""                          #change to field from form questions.table.question_text
close_date = ""                             #change to field from form questions.table.datetruevalueknown
num_of_choices = ""                         #change to field from form questions.table.num_of_choices
QSet = Question.objects.filter(question_use=question_use
    ).filter(forecast=forecast
    ).filter(question_type=question_type
    ).filter(question_text=question_text
    ).filter(close_date=close_date
    ).filter(num_of_choices=NoOfChoices
    ).filter(category=categoryObj)
question_id = Question.objects.get(id = QSet)

date_of_assessment = ""                     #change to field from form assessments.table.dateofassessment
details_of_assessment = ""                  #change to field from form assessments.table.assessement_details

#I AM STILL WORKING ON THIS QUERY
reader = Assessment.objects.filter(user_id = upload_user
    ).filter(question_id = question_id
    ).filter(date_of_assessment = date_of_assessment
    ).filter(details_of_assessment = details_of_assessment
    ).select_related().values(true_value, answer_text, option_text, operator)

# select_related(*fields)¶
# Returns a QuerySet that will “follow” foreign-key relationships, 
# selecting additional related-object data when it executes its query. 
# This is a performance booster which results in a single more complex 
# query but means later use of foreign-key 
# relationships won’t require database queries

# DEFINE INTERVALS FROM FORM
data=[]
intervals = 10                              #change to field from form 
mindata = 5
bins = [0 + x/intervals for x in range(0,intervals+1)]

for row in reader:
    # QUERY FORMAT: TRUEVALUE   PASSIGNED   VASSIGNED   OPERATOR   
    trueValue=float(row[0])
    pAssigned=float(row[1])
    vAssigned=float(row[2])
    operator=row[3]
    # POPULATING TABLE OF OBSERVED PROBABILITIES
    if operator == "EQ":
        if vAssigned == trueValue:
            data.append([trueValue,operator,vAssigned,pAssigned,1])
        else: 
            data.append([trueValue,operator,vAssigned,pAssigned,0])
    elif operator == "GE":
        if trueValue >= vAssigned:
            data.append([trueValue,operator,vAssigned,pAssigned,1])
        else: 
            data.append([trueValue,operator,vAssigned,pAssigned,0])
    elif operator == "LE":
        if trueValue <= vAssigned:
            data.append([trueValue,operator,vAssigned,pAssigned,1])
        else: 
            data.append([trueValue,operator,vAssigned,pAssigned,0])        
# USING THE RESULTS FROM THE PREVIOUS SECTION WE CAN ESTIMATE
# ALL THE SCORING RESULTS
counter=[]
totalcount = 0
totalcorr = 0
confidence = 0
calibration = 0
resolution = 0  
knowledge = 0
for j in range(len(bins)-1):
    bincorr = 0
    bincount = 0
    binprob = 0
    for i in range(len(data)):
        p = data[i]
        if bins[j] < p[3] and p[3] <= bins[j+1]:
            bincount += 1
            bincorr += p[4]
            binprob += p[3]           
    if bincount > 0:
        binmean = binprob/bincount
        binpercorr = bincorr/bincount
    else:
        binmean = bins[j]
        binpercorr = 0  
    if bins[j+1] <= 0.5:
        confidence = confidence + bincount*(binmean - binpercorr)
    else:
        confidence = confidence + bincount*(binpercorr - binmean)
    calibration = calibration + bincount*(binpercorr - binmean)**2
    totalcount = totalcount + bincount 
    totalcorr = totalcorr + bincorr
    counter.append([bins[j+1],binpercorr,bincount])    
for j in range(len(bins)-1):
    r = counter[j]
    resolution = resolution + r[2]*(totalcorr/totalcount-r[1])**2

# SUMMARY OF RESULTS     
confidence = confidence/totalcount
calibration = calibration / totalcount
resolution = resolution / totalcount
knowledge = totalcorr/totalcount*(1-totalcorr/totalcount)
brierscore = knowledge - resolution + calibration 

# WRITING OF RESULTS TO CSV
path = "C:/Users/raulgonzalez88/ScoringOut.csv"
with open(path,'w') as myfile:
    writer = csv.writer(myfile)
    for i in range(len(data)):
        writer.writerow(data[i])
    myfile.flush()
print ([confidence, calibration, resolution, knowledge, brierscore])    