# ERROR, WARNING LOGS

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

WarningQ ={0 : "The true value was updated for record in row ",
1 : "Insufficient data for the question, missing Question text, Category, NoOfChoices",
2 : "The units were updated for record in row ",
3 : "The units reported in the import file is different than the one in the database for record in row ",
4 : "A new category was created for record in row "}