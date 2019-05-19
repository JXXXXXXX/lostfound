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
    url(r'^login$',login_view,name='login'),     # 登陆界面
    url(r'^upload$',upload_view,name='upload'),  # 物品信息上传界面
    url(r'^object/(?P<object_id>[0-9]{20})$',objShowinfo_view,name='object'), # 物品信息显示页面
    url(r'^profile/(?P<nav_id>[0-4]{1})$',profile_view,name='profile'), # 个人中心-用户
    url(r'^quit$',quit_view,name='quit'), # 退出按钮
    url(r'^main$',main_view,name='main'), # 主界面
    url(r'^$',main_view),
    url(r'^sort/(?P<sort_id>[0-6]{1})$',sort_view,name='sort'), # 物品分类显示
    url(r'^complete_info$',complete_view),# 修改密码并完善个人信息
    url(r'search$',search_view,name='search'),    # 搜索框
                                    # 这里(搜索框)的正则表达式取消了开始的尖号(^)，
                                    # 这样所有以'search/'结尾的url,都能指向search_view
    url(r'^admin$',admin_view),# 修改密码并完善个人信息

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# "+static"是显示图片的需要（参考https://blog.csdn.net/c_beautiful/article/details/79755368

