"""searcher1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('fttb/', views.fttb_func, name='fttb_func'),
    url(r'check_ip_adr/$', views.check_ip_adr, name='check_ip_adr'),
    url(r'rez/$', views.rez, name='rez'),
    url(r'clear_data/$', views.clear_data, name='clear_data'),
    url(r'ok_daata/$', views.ok_daata, name='ok_daata'),

]
