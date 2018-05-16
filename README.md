
Installation for Linux

Step to set up the server to test your webpage.

1. Clone/download this repository
* Visit https://www.djangoproject.com/ for more information about the Django Web framework

2. Intall Anaconda in Linux https://www.anaconda.com/download/ (Choose python 2.7)
* Install Python packages **Django**, **psycopg2**, and other required packages 
  
3. Download the database: PostGreSQL:
* Download the latest version of PostGreSQL via https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
* In the installing process, set the default user and password to the ones under DATABASES in **setting.py**
* After installation, open the program pgAdmin 4 to activate the database
* Create a database “apa_db” and click "SAVE"

4. Open Anaconda Navigator again, click green arrow(root) to open a terminal. (Otherwise you need to add lots of stuff to the evnironmental path), navigator to where the manage.py is.

5. Run "python manage.py migrate"

6. Run "python manage.py runserver 0.0.0.0:8000"

7. Open a browser and do "localhost:8000/ucs"


Installation for Windows

Step to set up the server to test your webpage.

1.Clone/download this repository

2.Download Anaconda 4.4.0 for windows: https://www.continuum.io/downloads#windows (This is a python IDE)
* Install Python packages **Django**, **psycopg2**, and other required packages via the Environment in ANACONDA Navigator for installment 
  
3.Download the database: PostGreSQL:
* Download the latest version of PostGreSQL via https://www.enterprisedb.com/downloads/postgres-postgresql-downloads#windows
* In the installing process, set the default user and password to the ones under DATABASES in **setting.py**
* After installation, open the program pgAdmin 4 to activate the database
* Create a database “apa_db” and click "SAVE"

4.Open Anaconda Navigator again, click green arrow(root) to open a terminal. (Otherwise you need to add lots of stuff to the evnironmental path), navigator to where the manage.py is.

4.5 run "python manage.py migrate"

5.run "python manage.py runserver 0.0.0.0:8000"

6.open a browser and do "localhost:8000/ucs"
