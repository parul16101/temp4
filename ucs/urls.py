"""
Django urls for ucs project.

This module contains maping of all URLs and functions to be called in views after hitting respective URL.
"""
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url
from django.contrib import admin
from . import views

## @var urlpatterns
# This is an array which stores URL objects. Each URL object has a "Path", "Function to be called when this URL is hit" and "name" 
urlpatterns = [
    #User part
    url(r'^$', views.login, name="index"),
    url(r'^login/$', views.login, name="login"),
    url(r'^register/$', views.register, name="register"),
    url(r'^retrieve/$', views.retrieve, name="retrieve"),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^home_page/$', views.home_page, name="home_page"),
    url(r'^info_page/$', views.info_page, name="info_page"),
    url(r'^admin/', admin.site.urls),
    
    #Question part
    url(r'^create_question/$', views.create_question, name="create_question"),
    url(r'^search_question/$', views.search_question, name="search_question"),
    #url(r'^edit_question/(?P<question_id>[0-9]+)/$', views.edit_question, name="edit_question"),
    url(r'^edit_question/$', views.edit_question, name="edit_question"),
    url(r'^save_question/$', views.save_question, name="save_question"),
    
    #Assignment part
    url(r'^create_assignment/$', views.create_assignment, name="create_assignment"),
    url(r'^search_assignment/$', views.search_assignment, name="search_assignment"),
    url(r'^edit_assignment/$', views.edit_assignment, name="edit_assignment"),
    url(r'^show_assignment/$', views.show_assignment, name="show_assignment"),
    url(r'^do_assignment/$', views.do_assignment, name="do_assignment"),
    
    #Group part
    url(r'^create_group/$', views.create_group, name="create_group"),
    url(r'^search_group/$', views.search_group, name="search_group"),
    url(r'^edit_group/$', views.edit_group, name="edit_group"),  
    #Category part
    url(r'^manage_category/$', views.manage_category, name="manage_category"),
    
    #Evaluation part
    url(r'^plotting/$', views.plotting, name="plotting"),
    url(r'^result/$', views.result, name="result"),
    url(r'^scoring/$', views.scoring, name="scoring"),
    url(r'^scoring_test/$', views.scoring_test, name="scoring_test"),
    url(r'^batch_import/$', views.batch_import, name="batch_import"),
    url(r'^batch_export/$', views.batch_export, name="batch_export"),
    url(r'^download_log/$',views.download_log, name="download_log")
]# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
