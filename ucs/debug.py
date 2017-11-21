# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

    ErrorA = []
    WarningA = []
    ErrorQ = []
    WarningQ = []
    ErrorA.insert(0, "Insuficcient data for the assessment, missing NumOfPairs, Operator, or DateOfAssessment in row ")
    ErrorA.insert(1, "Number of choices cannot be equal to 1 (allowed options are 0 or greater than 1) for entry located in row ")
    ErrorA.insert(2, "Number of pairs needs to be same as the number of choices for entry located in row ")
    ErrorA.insert(3, "The number of data points read is different than the number of data points specified in the file, row  ")
    ErrorA.insert(4, "For a continuous distribution question the value assigned for operator should be LE or GE, row ")
    ErrorA.insert(5, "For a continuous distribution question with a LE operator, with increasing probabilities the assigned values \
        should be increasing, row ")
    ErrorA.insert(6, "For a continuous distribution question with a GE operator, with increasing probabilities the assigned values \
        should be decreasing, row ")
    ErrorA.insert(7, "For a continuous distribution question the probabilities  assigned should fall between 0 and 1, row " )
    ErrorA.insert(8, "For a multiple choice question the value assigned for operator should be EQ, row ")
    ErrorA.insert(9, "For multiple choice questions the probabilities assigned should fall between 0 and 1, row ")
    ErrorA.insert(10, "For multiple choice questions the value assigned should fall between 1 and the specified number of \
        choices, row ")
    WarningA.insert(0, "For multiple choice questions the sum of the assigned probabilites should add up to 1, row ")
    WarningA.insert(1,  "The assessment details were updated for record in row ")
    WarningA.insert(2, "The assessment details reported in the import file is different than the one in the database for \
        record in row ")
    ErrorQ.insert(0, "Question ID could not be found in the database for entry located in row ")
    ErrorQ.insert(1, "Number of choices cannot be equal to 1 (allowed options are 0 or greater than 1) for entry located in \
        row or missing information")
    WarningQ.insert(0, "The true value was updated for record in row ")
    WarningQ.insert(1, "Insufficient data for the question, missing Question text, Category, NoOfChoices")
    WarningQ.insert(2, "The units were updated for record in row ")
    WarningQ.insert(3, "The units reported in the import file is different than the one in the database for record in row ")
    WarningQ.insert(4, "A new category was created for record in row ")
