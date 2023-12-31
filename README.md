
Installation steps for the Probabilistic Forecast Tracking and Calibration Software System:

1. Clone or download this repository

2. Download and install Anaconda 4.4.0 from https://www.anaconda.com/download/ (Choose python 2.7)
* Install Python packages **Django**, **psycopg2**, and other required packages via the Environment in ANACONDA Navigator
* Visit https://www.djangoproject.com/ for more information about the Django Web framework
  
3. Download the database: PostGreSQL:
* Download the latest version of PostGreSQL via https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
* In the installing process, set password "admin" to the default user [postgres]
* After installation, open the program pgAdmin 4 to activate the database
* Create a database “apa_db” and click "SAVE"

4. Open Anaconda Navigator again, click green arrow(root) to open a terminal. (Otherwise you need to add lots of stuff to the evnironmental path), navigator to where the manage.py is.

5. Run "python manage.py makemigrations" to commit the database configuration

6. Run "python manage.py migrate" to apply the commits

7. Run "python manage.py createsuperuser" to set up a super admin for managing the raw database

8. Run "python manage.py runserver 0.0.0.0:8888"

9. Open Google Chrome and browse "localhost:8888/ucs"
