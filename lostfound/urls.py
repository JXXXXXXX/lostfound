"""lostfound URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from model.views import *

urlpatterns = [
    url('admin/', admin.site.urls), # django管理员界面
    url(r'^login$',login_view),     # 登陆界面
    url(r'^sort/login$',login_view),
    url(r'^upload$',upload_view),  # 物品信息上传界面
    url(r'^object/(?P<object_id>[0-9]{20})$',objShowinfo_view,name='object'), # 物品信息显示页面
    url(r'^profile/(?P<nav_id>[0-2]{1})$',profile_view,name='profile'), # 个人中心-用户
    url(r'^quit$',quit_view), # 退出按钮
    url(r'^main$',main_view), # 主界面
    url(r'^$',main_view),
    url(r'^sort/(?P<sort_id>[0-6]{1})$',sort_view,name='sort'), # 物品分类显示
    url(r'^complete_info$',complete_view),# 修改密码并完善个人信息

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# "+static"是显示图片的需要（参考https://blog.csdn.net/c_beautiful/article/details/79755368

