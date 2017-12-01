
Step to set up the server to test your webpage.

1.Clone/download this repository

2.Download Anaconda 4.4.0 for windows: https://www.continuum.io/downloads#windows (This is a python IDE)
* Install Python packages **Django**, **psycopg2**, **GDAL**, and other required packages via the Environment in ANACONDA Navigator for installment 
  
3.Download the database: PostGreSQL:
* Download the latest version of PostGreSQL via https://www.enterprisedb.com/downloads/postgres-postgresql-downloads#windows
* In the installing process, set the default password of user [postgresql] to ‘admin’
* After installation, open the program pgAdmin 4 to activate the database
* Create a database “apa_db” and click "SAVE"

4.Open Anaconda Navigator again, click green arrow(root) to open a terminal. (Otherwise you need to add lots of stuff to the evnironmental path), navigator to where the manage.py is.

4.5 run "python manage.py migrate"

5.run "python manage.py runserver 0.0.0.0:8000"

6.open a browser and do "localhost:8000/ucs"



