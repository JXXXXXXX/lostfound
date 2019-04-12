# -*- coding: UTF-8 -*-
from django.db import models

#数据库更新命令：
#！！每次对下面的数据库类进行修改后，就需要执行以下的两条指令对数据库进行更新
    #python manage.py makemigrations model
    #python manage.py migrate model

# Create your models here.
class User(models.Model):
    sno = models.CharField(primary_key=True,max_length=10)  #学号-主键
    pwd = models.CharField(max_length=20)                   #密码
    name = models.CharField(max_length=10)                  #姓名
    phone = models.CharField(max_length=15,null=True)       #电话
    email = models.EmailField(max_length=50,null=True)      #邮箱
    tag = models.BooleanField(default=False)                #标识：tag=True 为管理员；tag=false 为普通用户

class Object(models.Model):
    id = models.CharField(primary_key=True,max_length=20)   #物品编号id 由上传的时间组成
    name = models.CharField(max_length=10)                  #名称
    time = models.DateField()                               #捡到/丢失日期
    position = models.CharField(max_length=100)             #捡到/丢失地点
    dscp = models.CharField(max_length=200)                 #描述
    img  = models.ImageField(upload_to="img/object")        #图片
    tag = models.BooleanField(default=False)                #标识：tag=false lost 寻物启事；tag=true found 失物招领
    state = models.IntegerField()                           # state=0:未审核；state=-1:审核不通过
                                                            # state=1 已审核，未被领取/捡到；state=2:已审核，被领取/捡到
    class Meta:
        ordering = ['id']

class UserObject(models.Model):
    object = models.ForeignKey(Object,
                               on_delete=models.CASCADE,)   #物品-外键
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,)     #用户-外键
    time = models.DateTimeField(auto_now=True)              #信息提交时间
    class Meta:
        unique_together=("object","user")                   #物品和用户联合——主键

class AllSort(models.Model):
    id = models.AutoField(primary_key=True)                 #类别编号-主键(自增)
    name = models.CharField(max_length=10)                  #物品分类的类别名称

class SortObject(models.Model):
    sort = models.ForeignKey(AllSort,
                             on_delete=models.CASCADE,)     #类别-外键
    object = models.ForeignKey(Object,
                               on_delete=models.CASCADE,)   #物品-外键
    class Meta:
        unique_together=("sort","object")                   #类别和物品联合主键

class TakenRecord(models.Model):#认领记录（认领是双向的
    user1 = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="User1",)        #信息发布者
    user2 = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="User2")         #提供失物 / 认领者
    object = models.ForeignKey(Object,
                               on_delete=models.CASCADE,)   #物品
    time = models.DateTimeField(auto_now_add=True)                           #认领时间
    tag = models.BooleanField(default=False)                #（user2）标识 tag=false lost 丢失的人（认领者）
                                                            # tag=true found 捡到的人
    class Meta:
        unique_together=("user1","user2","object")          #用户1、用户2、物品共同作为主键

class feedbackType(models.Model):# 反馈信息类型
    id = models.AutoField(primary_key=True)                 # 类型编号
    type = models.CharField(max_length=100)                 # 类型名称

class obj_feedbackType(models.Model):
    # 物品-反馈类型，每一个审核未通过的物品(object.state=-1)
    # 都与一个反馈信息的类型相关联，以告知用户为什么审核不通过
    object = models.ForeignKey(Object,
                               on_delete=models.CASCADE,)   # 物品(这里加入的物品应该state=-1)
    feedbackType = models.ForeignKey(feedbackType,
                            on_delete=models.CASCADE,)      # 反馈信息

    other_info = models.CharField(max_length=100, null=True)# 备注：当类型为'其他'时，管理员可以输入自定义的反馈信息
    class Meta:
        unique_together=("object","feedbackType")           # 物品-反馈信息联合主键