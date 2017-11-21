import csv
    #from ucs.models import Question, Assessment, Category

ErrorA=[]
WarningA=[]
ErrorQ=[]
WarningQ=[]
ErrorA.insert(0, "Insuficcient data for the assessment, missing NumOfPairs, Operator, or DateOfAssessment in row ")
ErrorA.insert(1, "Number of choices cannot be equal to 1 (allowed options are 0 or greater than 1) for entry located in row ")
ErrorA.insert(2, "Number of pairs needs to be same as the number of choices for entry located in row ")
ErrorA.insert(3, "The number of data points read is different than the number of data points specified in the file, row  ")
ErrorA.insert(4, "For a continuous distribution question the value assigned for operator should be LE or GE, row ")
ErrorA.insert(5, "For a continuous distribution question with a LE operator, with increasing probabilities the assigned values should be increasing, row ")
ErrorA.insert(6, "For a continuous distribution question with a GE operator, with increasing probabilities the assigned values should be decreasing, row ")
ErrorA.insert(7, "For a continuous distribution question the probabilities  assigned should fall between 0 and 1, row " )
ErrorA.insert(8, "For a multiple choice question the value assigned for operator should be EQ, row ")
ErrorA.insert(9, "For multiple choice questions the probabilities assigned should fall between 0 and 1, row ")
ErrorA.insert(10, "For multiple choice questions the value assigned should fall between 1 and the specified number of choices, row ")
WarningA.insert(0, "For multiple choice questions the sum of the assigned probabilites should add up to 1, row ")
WarningA.insert(1,  "The assessment details were updated for record in row ")
WarningA.insert(2, "The assessment details reported in the import file is different than the one in the database for record in row ")
ErrorQ.insert(0, "Question ID could not be found in the database for entry located in row ")
ErrorQ.insert(1, "Number of choices cannot be equal to 1 (allowed options are 0 or greater than 1) for entry located in row or missing information")
WarningQ.insert(0, "The true value was updated for record in row ")
WarningQ.insert(1,"The true value reported in the import file is different than the one in the database for record in row ")
WarningQ.insert(2, "The units were updated for record in row ")
WarningQ.insert(3, "The units reported in the import file is different than the one in the database for record in row ")
WarningQ.insert(4, "A new category was created for record in row ")

# List of encountered errors and warnings in the process to be printed
ErrorLogQ = []
WarningLogQ = []
ErrorLogA = []
WarningLogA =[]

# Data Reading
#path = "E:/test/TEST 2/IMPORTQ.csv"
#path = "C:/Users/raulgonzalez88/IMPORTQ.csv"
path = "C:/Users/Jason/Dropbox/Code/Apache/test/IMPORTQ.csv"
reader = csv.reader(open(path),delimiter=",")
header=next(reader)
data=[]

#user_id = request.session.get("userId")
#if not user_id:
#    return redirect(reverse("login"))
#message = None

for row in reader:
    ErrorQv=0
    WarningQv=0
    # ********************** QUESTION INFORMATION VALIDATION **********************
    # Check and validate all the question information before it gets stored into the
    # database. There are 2 associated errors with the question data that will prevent
    # questions from being imported, while there are 5 warnings. A warning will
    # still be able to store data in the database
#    if row[0] != '':
#        QuestionID=float(row[0])
#        #Check question exists in the database
#        Q = Question.objects.filter(id=QuestionID)
#            if len(Q) == 0!:
#                ErrorQ +=1
#                ErrorLogQ.insert(reader.line_num, ErrorQ[4] + str(reader.line_num))
    if ErrorQv == 0:
        if row[6] != '' and row[5] != '' and row[4] != '':
        ## VARIABLE NAME IN PYTHON  VARIABLE NAME IN DJANGO
		## ADD A VALIDATION FOR QUESTIONS THAT ARE FORECAST
            QuestionUse=str(row[1]) ## id *
            QForecast=str(row[2])   ## forecast *
            QuestionType=str(row[3])    ## question_type *
            NoOfChoices=float(row[4])   ## num_of_choices *
            QCategory=str(row[5])   ## category *
            QuestionText=str(row[6])    ## question_text *
            DateTrueValueKnown=str(row[7])    ## close_date *
            TrueValue=float(row[8])     ## true_value *
            Units=str(row[9])   ## unit *
            QuestionSource=str(row[10])     ## question_source
            AllowAssessment=str(row[11])    ## allow_assessment
        else:
            ErrorQv +=1
            ErrorLogQ.insert(reader.line_num, ErrorQ[1] + str(reader.line_num))

            #Check category exists in the database
            #Q = Category.objects.filter(category_text=QCategory)
#        if len(Q) == 0:
#            WarningQv +=1
#            WarningLogQ.insert(reader.line_num, WarningQ[0] + str(reader.line_num))
#            NewCategory = Category(category_text = QCategory)
#            newCategory.save()
#
#    if ErrorQv == 0:
#        ## Check if question exists in database
#        Q = Question.objects.filter(
#            question_type=QuestionType
#            ).filter(close_date=DateTrueValueKnown
#            ).filter(category=QCategory
#            ).filter(num_of_choices=NoOfChoices
#            )
#        if len(Q) == 0:
#           # Question does not exist in the database add question
#           # UPDATE FIELDS
#            newQuestion = Question(question_text = QuestionText,
#                            uploader_id = user_id,
#                            upload_date = upload_date,
#                            close_date = DateTrueValueKnown,
#                            num_of_choices = NoOfChoices,
#                            category = QCategory,
#                            question_type = QuetionType,
#                            forecast = QForecast
#                            true_value = TrueValue
#                            unit = Units,
#                            question_source = QuestionSource,
#                            allow_assessment = AllowAssessment
#                            )
#                            newQuestion.save();
#            QuestionID=Q.values(id)
#        else:
#            # Question exists then update true vlaue/units
#            if TrueValue != '':
#                QTrueValue=Q.filter(true_value = TrueValue)
#                TrueValueSystem=QTrueValue.values(true_value)
#                if TrueValueSystem == '':
#                    Q.update(true_value = TrueValue)
#                    WarningQv +=1
#                    WarningQ.insert(reader.line_num, WarningQ[0] + str(reader.line_num))
#                elif TrueValueSystem != TrueValue:
#                    WarningQ +=1
#                    WarningQ.insert(reader.line_num, WarningQ[1] + str(reader.line_num))
#            if Units != '':
#                QTrueUnits=Q.filter(unit = Units)
#                TrueUnitsSystem=QTrueUnits.values(unit)
#                if TrueUnitsSystem == '':
#                    Q.update(unit = Units)
#                    WarningQv +=1
#                    WarningQ.insert(reader.line_num, WarningQ[2] + str(reader.line_num))
#                elif TrueUnitsSystem != TrueValue:
#                    WarningQv +=1
#                    WarningQ.insert(reader.line_num, WarningQ[3] + str(reader.line_num))

    ErrorAv=0
    WarningAv=0
    # ********************** ASSESSMENT INFORMATION VALIDATION **********************
    # Check and validate all the assessment information before it gets stored into the
    # database. There are 10 associated errors with the assessment data that will prevent
    # assessments from being imported, while there is only 1 warning. A warning will
    # still be able to store data in the database

    NumOfPairs=int(row[15])
    #Make a comment regarding how this cant be empty
    NumOfChoices=float(row[4])
    DateOfAssessment=str(row[12])
    Operator=str(row[13])
    DetailsOfAssessment=str(row[14])

    #VALIDATION OF ASSESSMENT INPUT/OPTIONS
    # Validate that NumOfPairs, Operator, or DateOfAssessment are not missing
    if NumOfPairs == '' or Operator == '' or DateOfAssessment == '':
        ErrorAv +=1
        ErrorLogA.insert(reader.line_num, ErrorA[0] + str(reader.line_num))
    # Validate that NumOfChoices can only be 0 or greater than 1
    if NumOfChoices < 0 or NumOfChoices == 1:
        ErrorAv +=1
        ErrorLogA.insert(reader.line_num, ErrorA[1] + str(reader.line_num))
    # Check for insufficient data when NumOfPairs is different than NumOfChoices for discrete
    elif NumOfChoices == 0:
        # Check that for the continuous case NumOfPairs is greater than 1
        if NumOfPairs <= 0:
            ErrorAv +=1
            ErrorLogA.insert(reader.line_num, ErrorA[2] + str(reader.line_num))
    else:
        # Check that for discrete the NumOfChoices is equal to NumOfPairs
        if NumOfPairs != NumOfChoices:
            ErrorAv +=1
            ErrorLogA.insert(reader.line_num, ErrorA[2] + str(reader.line_num))
    #VALIDATION OF SUFFICIENT DATA
    prob = []
    val=[]
    for i in range (0,NumOfPairs):
        if row[16+2*i] == '' or row[17+2*i]== '':
            ErrorAv +=1
            ErrorLogA.insert(reader.line_num, ErrorA[3] + str(reader.line_num))
        else:
            prob.insert(reader.line_num,float(row[16+2*i]))
            val.insert(reader.line_num,float(row[17+2*i]))
    #VALIDATION OF AVAILABLE ASSESSMENT DATA
    # Sort both Probabilities and Values for further validation if there are more than
    # 2 pairs of assessments
    if sum(prob)>2:
        prob, val = (list(x) for x in zip(*sorted(zip(prob, val))))
    if NumOfChoices > 1:
        # Check that the operator is not different than EQ or empty
        if Operator != "EQ":
            ErrorAv += 1
            ErrorLogA.insert(reader.line_num, ErrorA[8] + str(reader.line_num))
        # Warn user that the sum is not 1
        if sum(prob) !=1:
            WarningAv += 1
            WarningLogA.insert(reader.line_num, WarningA[0] + str(reader.line_num))
        # Check that all probabilities are between 0 and 1
        if sum([i > 1 for i in prob]) > 1:
            ErrorAv +=1
            ErrorLogA.insert(reader.line_num, ErrorA[9] + str(reader.line_num))
        if sum([i < 0 for i in prob]) > 1:
            ErrorAv +=1
            ErrorLogA.insert(reader.line_num, ErrorA[9] + str(reader.line_num))
        # Check that all values are between 1 and the NumOfChoices
        if sum([i > NumOfChoices for i in val]) > 1:
            ErrorAv +=1
            ErrorLogA.insert(reader.line_num, ErrorA[10] + str(reader.line_num))
    elif NumOfChoices == 0:
        # Check that for LE everything is ascending
        if Operator == "LE" and NumOfPairs > 2:
            if sum([x<y for x, y in zip(val, val[1:])]) > 0:
                ErrorAv +=1
                ErrorLogA.insert(reader.line_num, ErrorA[5] + str(reader.line_num))
        # Check that for GE everything is ascending
        elif Operator == "GE" and NumOfPairs > 2:
            if sum([x>y for x, y in zip(val, val[1:])]) > 0:
                ErrorAv +=1
                ErrorLogA.insert(reader.line_num, ErrorA[6] + str(reader.line_num))
        # Check that the operator is not EQ or empty
        else:
            ErrorAv +=1
            ErrorLogA.insert(reader.line_num, ErrorA[4] + str(reader.line_num))
        # Check that all probabilities are between 0 and 1
        if sum([i > 1 for i in prob]) > 0:
            ErrorAv +=1
            ErrorLogA.insert(reader.line_num, ErrorA[7] + str(reader.line_num))
        if sum([i < 0 for i in prob]) > 0:
            ErrorAv +=1
            ErrorLogA.insert(reader.line_num, ErrorA[7] + str(reader.line_num))

    if ErrorAv == 0:
        for i in range (0, NumOfPairs):
            data.append([QuestionUse, QForecast, QuestionType,QuestionText, NoOfChoices, Operator, prob[i], val[i]])

#    if ErrorAv == 0:
#        for i in range (0, NumOfPairs):
#            ## Check if Assessments exists in database
#            A = Assessments.objects.filter(
#                user_id = user_id
#                ).filter(question_id = QuestionID
#                ).filter(prob = Prob[i]
#                ).filter(value = Val[i]
#                ).filter(date_of_assessment = DateOfAssessment)
#                ).filter(details_of_assessment = DetailsOfAssessment)
#                )
#            if len(Q) == 0:
#                #Question does not exist in the database add question
#                newAssessment = Assessment(question_id=QuestionID
#                                user_id = user_id
#                                answer_text = Prob[i]
#                                option_text = Val [i]
#                                operator = Operator
#                                date_of_assessment = DateOfAssessment
#                                details_of_assessment = DetailsOfAssessment
#                                )
#                newAssessment.save();
#            else:
#                # Question exists then update true vlaue/units
#                if DetailsOfAssessment != '':
#                    AssessmentDetails=A.filter(details_of_assessment = DetailsOfAssessment)
#                    AssessmentDetailsSystem=AssessmentDetails.values(details_of_assessment)
#                    if AssessmentDetailsSystem == '':
#                        A.update(details_of_assessment = DetailsOfAssessment)
#                        WarningQ +=1
#                        WarningQ.insert(reader.line_num, WarningQ[1] + str(reader.line_num))
#					elif TrueValueSystem != TrueValue:
#                        WarningQ +=1
#                        WarningQ.insert(reader.line_num, WarningQ[2] + str(reader.line_num))

#    if ErrorQv == 0:
#        print ("Success question validation data in row " + str(reader.line_num))
#    if ErrorAv == 0:
#        print ("Success assessment validation data in row " + str(reader.line_num))

#path = "C:/Users/raulgonzalez88/OUTPUTQ.csv"
path = "C:/Users/Jason/Dropbox/Code/Apache/test/OUTPUTQ.csv"
with open(path,'w') as myfile:
    writer = csv.writer(myfile, delimiter=',', quotechar='"')
    for i in range(len(data)):
        print(data[i])
        writer.writerow(data[i])
        myfile.flush()
