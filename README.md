
This is Linux Version

Step to set up the server to test your webpage.

1. Clone/download this repository
* Visit https://www.djangoproject.com/ for more information about the Django Web framework

2. Intall Anaconda in Linux https://www.anaconda.com/download/ (Choose python 2.7)
* Install Python packages **Django**, **psycopg2**, **GDAL**, and other required packages 
  
3. Download the database: PostGreSQL:
* Download the latest version of PostGreSQL via https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
* In the installing process, set the default password of user [postgresql] to ‘admin’
* After installation, open the program pgAdmin 4 to activate the database
* Create a database “apa_db” and click "SAVE"

4. Open Anaconda Navigator again, click green arrow(root) to open a terminal. (Otherwise you need to add lots of stuff to the evnironmental path), navigator to where the manage.py is.

5. Run "python manage.py migrate"

6. Run "python manage.py runserver 0.0.0.0:8000"

7. Open a browser and do "localhost:8000/ucs"
