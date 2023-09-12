"""
WSGI config for ucs project.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

#print "Hello"

from django.core.wsgi import get_wsgi_application

path='/home/shared/Apache/'
if path not in sys.path:
	sys.path.append('/home/shared/anaconda64/envs/web_env/lib/python2.7/site-packages')
	sys.path.append('/home/shared/anaconda64/lib')
	sys.path.append(path)
	
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ucs.settings")
## @var application
# This module exposes the WSGI callable as a module-level variable named ``application``.
application = get_wsgi_application()
