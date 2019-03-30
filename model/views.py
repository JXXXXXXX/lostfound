from django.shortcuts import render_to_response,HttpResponse,redirect
from model import forms,models
import datetime

# 分类缩写与sort_id的对应关系字典
sort={'qt':6,
      'shyp':5,
      'dzyp':4,
      'ywpj':3,
      'sbwj':2,
      'zjxj':1,}

# 登陆页面
def login_view(request):
    if request.method == "POST":
        form = forms.login_form(request.POST)
        if form.is_valid():
            # 表单合法，则会把数据放在表单的cleaned_data中
            cd = form.cleaned_data
            username=cd['username']
            password=cd['password']
            try:
                user_db = models.User.objects.get(sno=username)#连接数据库检查密码正确性
                if user_db.pwd == password:
                    # 密码正确
                    request.session["sno"]=user_db.sno # 记录用户sno
                    return redirect('/main') # 登陆成功 返回主界面
                        # redirect 只能通过session传递参数
                else:
                    # 密码错误
                    return HttpResponse("password error or user dont exist")
            except models.User.DoesNotExist:
                # 用户不存在
                return HttpResponse("password error or user dont exist")
        else:
            # 表单不合法
            return HttpResponse("form invalid")
    else:
        # 检查是否已经登陆
        if 'sno' in request.session:
            # sno在session中表面已经登陆
            return render_to_response('afterlogin.html')
        else:
            form=forms.login_form()
            return render_to_response('login_form.html',{'form':form})

def login2_view(request):
    if request.method == "POST":
        form = forms.login_form(request.POST)
        if form.is_valid():
            # 表单合法，则会把数据放在表单的cleaned_data中
            cd = form.cleaned_data
            username=cd['username']
            password=cd['password']
            try:
                user_db = models.User.objects.get(sno=username)#连接数据库检查密码正确性
                if user_db.pwd == password:
                    # 密码正确
                    request.session["sno"]=user_db.sno # 记录用户sno
                    return render_to_response('afterlogin.html') # 登陆成功
                        # redirect 只能通过session传递参数
                else:
                    # 密码错误
                    return HttpResponse("password error or user dont exist")
            except models.User.DoesNotExist:
                # 用户不存在
                return HttpResponse("password error or user dont exist")
        else:
            # 表单不合法
            return HttpResponse("form invalid")
    else:
        # 检查是否已经登陆
        if 'sno' in request.session:
            # sno在session中表面已经登陆
            return render_to_response('afterlogin.html')
        else:
            form=forms.login_form()
            return render_to_response('log_in.html',{'form':form})

# 信息上传页面——objUpload.html
def objUpload_view(request):
    if request.method=="POST":
        # 获取用户输入后的POST表单
        form=forms.objUpload_form(request.POST,request.FILES)# request.FILES是获取imagefield的要求，否则获取不到图片

        # 检查表单的合法性
        if form.is_valid():
            obj=models.Object()             # 创建上传的物品的对象
            user_obj=models.UserObject()    # 创建用户-物品对象
            try:
                # ！其实这里有问题，假如用户随意输入的学号是存在于数据库中的，那提交的用户就会变成那个学号，而不一定是登陆的用户本身
                user_db = models.User.objects.get(sno=request.session['sno']) #request.session通过cookie记录用户状态
                user_obj.user=user_db

                # 输入物品信息
                nowtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
                obj.id = nowtime                            # 为物品生成一个当前时间的id，作为主键
                obj.name = form.cleaned_data['name']
                input_date = form.cleaned_data['time']
                obj.time = datetime.date(datetime.datetime.now().year,
                                         input_date.month,
                                         input_date.day)
                # 因为表单输入没有设置year（默认year=1900）需要重新设置
                # datetime 对象是不可修改的（not writable），实现赋值需要新的date对象
                obj.position = form.cleaned_data['position']
                obj.dscp = form.cleaned_data['dscp']
                obj.tag = form.cleaned_data['tag']
                obj.state = 0  # state=0 未审核状态
                if form.cleaned_data['img']:
                    # 如果有图片上传则执行以下部分
                    obj.img = form.cleaned_data['img']
                    obj.img.name = nowtime+".jpg"# 将图片名称修改为物品id
                obj.save()# 上传物品到数据库

                obj_db = models.Object.objects.get(id=nowtime)# 检查是否物品信息是否上传到数据库（通过搜索数据库中，有无id=nowtime的物品，若没有会被except处理
                user_obj.object=obj_db
                user_obj.save()# 上传 用户-物品记录
                return HttpResponse("Upload successfully.")
            except models.User.DoesNotExist:
                # 用户不存在
                return HttpResponse("User dont exist.")
            except models.Object.DoesNotExist:
                # 物品信息没有存入数据库
                return HttpResponse("Upload error.")
        else:
            #表单不合法
            return HttpResponse("Input invalid.")
    else:
        # 处理非POST的情况,返回表单页面，用户输入数据
        context = {}
        try:
            sno_login = request.session["sno"]
        except KeyError:
            return render_to_response('objUpload.html', context)
        # 已经登陆
        context['user']=models.User.objects.get(sno=sno_login)
        form = forms.objUpload_form
        context['form']=form
        return render_to_response('objUpload.html',context)

# 信息上传页面——re_lost.html
def objUpload2_view(request):
    if request.method=="POST":
        # 1.创建将要上传的'物品'对象(obj)，并将之上传到数据库
        # 2.更新【物品-用户】表和【分类-物品】表

        # 获取用户输入后的POST表单
        form=forms.objUpload2_form(request.POST,request.FILES)# request.FILES是获取imagefield的要求，否则获取不到图片

        # 检查表单的合法性
        if form.is_valid():
            obj=models.Object()             # 创建上传的物品的对象
            user_obj=models.UserObject()    # 创建用户-物品对象
            sort_obj=models.SortObject()    # 创建分类-物品对象
            try:
                # ！其实这里有问题，假如用户随意输入的学号是存在于数据库中的，那提交的用户就会变成那个学号，而不一定是登陆的用户本身
                user_db = models.User.objects.get(sno=request.session['sno']) #request.session通过cookie记录用户状态
                user_obj.user=user_db

                # 输入物品信息
                nowtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
                obj.id = nowtime                            # 为物品生成一个当前时间的id，作为主键
                obj.name = form.cleaned_data['name']
                obj.time = form.cleaned_data['time']
                obj.position = form.cleaned_data['position']
                obj.dscp = form.cleaned_data['dscp']
                if form.cleaned_data['tag']=='lost':
                    obj.tag=False
                else:
                    obj.tag = True
                obj.state = 0  # state=0 未审核状态
                if form.cleaned_data['img']:
                    # 如果有图片上传则执行以下部分
                    obj.img = form.cleaned_data['img']
                    obj.img.name = nowtime+".jpg"# 将图片名称修改为物品id
                obj.save()# 上传物品到数据库
                # 根据物品的种类，上传sortobject

                obj_db = models.Object.objects.get(id=nowtime)# 检查是否物品信息是否上传到数据库（通过搜索数据库中，有无id=nowtime的物品，若没有会被except处理
                user_obj.object=obj_db
                user_obj.save()# 上传 用户-物品记录

                sort_id = sort[form.cleaned_data['categary']]
                sort_db = models.AllSort.objects.get(id=sort_id)
                sort_obj.sort = sort_db
                sort_obj.object = obj_db
                sort_obj.save()# 上传 分类-物品记录

                return HttpResponse("Upload successfully.")
            except models.User.DoesNotExist:
                # 用户不存在
                return HttpResponse("User dont exist.")
            except models.AllSort.DoesNotExist:
                # 分类不存在
                return HttpResponse("Sort dont exist.")
            except models.Object.DoesNotExist:
                # 物品信息没有存入数据库
                return HttpResponse("Upload error.")
        else:
            #表单不合法
            print(form.errors)
            return HttpResponse("Input invalid.")
    else:
        # 处理非POST的情况,返回表单页面，用户输入数据
        context = {}
        try:
            sno_login = request.session["sno"]
        except KeyError:
            return render_to_response('re_lost.html', context)
        # 已经登陆
        context['user']=models.User.objects.get(sno=sno_login)
        form = forms.objUpload_form
        context['form']=form
        return render_to_response('re_lost.html',context)

#物品详细信息显示
def objShowinfo_view(request,object_id):
    # 1.获得【物品】和发布该信息的【用户】
    # 2.根据【登陆情况】【物品是否审核】及【登陆用户的权限】三者来决定信息的显示规则

    # step1
    obj_db = models.Object.objects.filter(id=object_id)
    #使用get如果味查询到会抛出异常，filter会返回空的[]
    if(len(obj_db)==0):
        return HttpResponse("this page does not exist!")
    obj = obj_db[0]
    #列表中的第一个对象
    userobj_db = models.UserObject.objects.get(object=obj.id)
    user_db = models.User.objects.get(sno=userobj_db.user.sno)
    #user在UserObject中定义为外键,userobj_db.user返回的是User对象
    context={}
    context['user']=user_db
    context['obj']=obj
    #contexet为一个字典

    # step2
    show_obj=False  # 物品信息显示标记 初始False
    show_user=False # 用户信息显示标记 初始False
    if 'sno' in request.session:
        # 已登录
        user_login = models.User.objects.get(sno=request.session['sno']) # 获得已登录用户信息
        if user_login.tag:
            # tag==True 管理员
            # 显示所有
            show_obj=True
            show_user=True
        else:
            # tag==False 普通用户
            if obj.state>0:
                # 通过审核
                # 显示所有
                show_obj = True
                show_user = True
            # else:
            # 未通过审核，都为False
    else:
        # 未登陆
        # 仅显示物品信息
        show_obj=True

    context['show_obj']  = show_obj
    context['show_user'] = show_user
    return render_to_response("objShowinfo.html",context)

#物品列表显示
def objList_view(request):
    #审核通过的物品,按提交时间(id)降序
    obj_db = models.Object.objects.filter(state=1).order_by('-id')
    if len(obj_db)==0:
        return HttpResponse('no valid information of objects')
    context={'context':obj_db}

    return render_to_response("objList.html",context)

# 个人中心-用户
def profile_view(request):
    # 1.通过request.session获得登陆用户
    # 2.显示用户得个人信息
    # 3.利用"二级页面"的逻辑，显示用户发表过的信息记录
    context = {}  # form字典
    try:
        sno_login = request.session["sno"]
    except KeyError:
        # 未登录的情况下，使用session会报错：KeyError
        return render_to_response("profile.html", context)
    # 已登录
    try:
        # step1
        user_login = models.User.objects.get(sno=sno_login)
        context["user"] = user_login  # 将'用户'加入字典中
        # step2
        userobject_db = models.UserObject.objects.filter(user=user_login)
        objs = []
        for item in userobject_db:
            objs.append(item.object) # 将所有用户的物品记录放到objs中
        if len(objs) == 0:
            context["no_history"] = True
        else:
            context["objs"] = objs  # 将'记录'加入字典字典
    except models.User.DoesNotExist:
            # 数据库没有该用户
        return HttpResponse("The user (id="+request.session["sno"]+") doesn't exist in database.")
    return render_to_response("profile.html", context)

# 退出按钮
def quit_view(request):
    # 1.清除用户登陆，包括cookie
    # 2.退出后，跳转到主界面（现在先跳转到登陆界面
    request.session.flush()
    return redirect("/main")

# 主界面
def main_view(request):
    context={}
    # 选择最近的【失物招领】和【寻物启事】各8条
    try:
        lost = models.Object.objects.filter(tag=False)
        found = models.Object.objects.filter(tag=True)
        if len(lost)>8:
            num_lost = 8
        else:
            num_lost = len(lost)
        if len(found)>8:
            num_found = 8
        else:
            num_found = len(found)
        if num_lost!=0:
            context['lost']=lost[0:num_lost-1]
        if num_found!=0:
            context['found']=found[0:num_found-1]

    except models.Object.DoesNotExist:
        return HttpResponse("DoesNotExist Error")
    if 'sno' in request.session:
        # 用户已登陆
        context['sno']=request.session['sno']
    return render_to_response("index.html",context)

# 分类显示
def sort_view(request,sort_id):
    # 1.根据传递的url sort/(sort_id：一位！字符！),选出所有的物品
    # 2.把通过审核的物品加入显示list

    # step1
    context={}
    try:
        # 注意返回的sort_id 是个字符，不是数字
        # print(sort_id.__class__)
        if (sort_id=='0'):  # 总览：显示所有分类的object
            sortobj_db = models.SortObject.objects.all()
        else:  # 选出特点类型的物品
            sort_for_search = models.AllSort.objects.get(id=sort_id)
            sortobj_db = models.SortObject.objects.filter(sort=sort_for_search)
    except models.SortObject.DoesNotExist:
        return HttpResponse("models DoesNotExist ERROR")
    except models.AllSort.DoesNotExist:
        return HttpResponse("models DoesNotExist ERROR")

    objs = []
    for item in sortobj_db:
        # step2
        if item.object.state>0: # 筛选通过审核的
            objs.append(item.object) # 将所有用户的物品记录放到objs中
    if len(objs) == 0:
        context["no_history"] = True
    else:
        context["context"] = objs  # 将'记录'加入字典字典

    return render_to_response('objList.html',context)