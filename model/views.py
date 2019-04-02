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

# 登陆页面（新）
def login_view(request):
    # 检查输入的学号/密码正确性
    # 若正确，设置session['sno']
    # 若错误，设置错误类型
    # 返回到登陆界面，错误提示也显示在登陆界面
    context = {}
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
                    if user_db.pwd == user_db.sno:
                        #如果密码为初始密码,则要求用户修改密码并完善个人信息
                        return redirect('/complete_info')
                    if 'errortype' in request.session:
                        # 若存在错误标记，则删除
                        del request.session['errortype']
                    return redirect('/main') # 登陆成功-跳转到主界面
                        # redirect 只能通过session传递参数
                else:
                    # 密码错误
                    context['error']=True
                    context['pwd_error']=True
                    return render_to_response('log_in.html',context)
            except models.User.DoesNotExist:
                # 用户不存在
                context['error'] = True
                context['no_user']=True
                return render_to_response('log_in.html',context)
        else:
            # 表单不合法
            context['error'] = True
            context['form_rror']=True
            return render_to_response('log_in.html', context)
    else:
        # 非post方式访问log_in.html
        # 1.检查是否已经登陆
        if 'sno' in request.session:
            # 已经登陆-返回主界面
            user_login = models.User.objects.get(sno=request.session['sno'])
            context['user_sno'] = user_login.sno
            context['user_name'] = user_login.name
            return render_to_response('index.html',context)
        else:
            # 未登陆
            return render_to_response('log_in.html')

# 信息上传页面——upload.html
def upload_view(request):
    if request.method=="POST":
        # 1.创建将要上传的'物品'对象(obj)，并将之上传到数据库
        # 2.更新【物品-用户】表和【分类-物品】表

        # 获取用户输入后的POST表单
        form=forms.objUpload_form(request.POST,request.FILES)# request.FILES是获取imagefield的要求，否则获取不到图片

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
            return HttpResponse("Input invalid.")
    else:
        # 处理非POST的情况,返回表单页面，用户输入数据
        context = {}
        try:
            sno_login = request.session["sno"]
        except KeyError:
            return render_to_response('upload.html', context)
        # 已经登陆
        context['user']=models.User.objects.get(sno=sno_login)
        return render_to_response('upload.html', context)

#物品详细信息显示
def objShowinfo_view(request,object_id):
    # 1.获得【物品】和发布该信息的【用户】
    # 2.根据【登陆情况】【物品是否审核】及【登陆用户的权限】三者来决定信息的显示规则

    # 管理员按钮处理
    if request.method == "POST":
        command1 = request.POST.getlist("delete")
        command2 = request.POST.getlist("pass")
        if len(command1)>0:
            p=models.Object.objects.get(id=str(object_id))
            p.state=-1
            p.save()

        elif len(command2)>0:
            p=models.Object.objects.get(id=str(object_id))
            p.state=1
            p.save()

    # -----------------主要部分---------------------

    # step1
    obj_db = models.Object.objects.filter(id=object_id)
    #使用get如果味查询到会抛出异常，filter会返回空的[]
    if(len(obj_db)==0):
        return HttpResponse("this page does not exist!")
    obj = obj_db[0]
    #列表中的第一个对象
    userobj_db = models.UserObject.objects.get(object=obj.id)   # 上传的物品
    user_db = models.User.objects.get(sno=userobj_db.user.sno)  # 上传者
    #user在UserObject中定义为外键,userobj_db.user返回的是User对象
    context={}
    context['user']=user_db
    context['obj']=obj

    # 确定物品的类别
    try:
        sortobj_db = models.SortObject.objects.get(object=obj)
        sort = sortobj_db.sort
        context['sort'] = sort.name
    except models.SortObject.DoesNotExist:
        HttpResponse("models.SortObject.DoesNotExist")
    # step2
    show_obj=False  # 物品信息显示标记 初始False
    show_user=False # 用户信息显示标记 初始False
    if 'sno' in request.session:    # 'sno'是当前登陆的用户，是查看这条信息的人
        # 已登录
        user_login = models.User.objects.get(sno=request.session['sno']) # 获得已登录用户信息
        if user_login.tag:
            # tag==True 管理员
            # 显示所有
            show_obj=True
            show_user=True
        else:
            # tag==False 普通用户
            # 若上传者和查看者时同一人，也可以直接查看
            if obj.state>0 or request.session['sno']==user_db.sno:
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
        user_login = []

    context['show_obj']  = show_obj
    context['show_user'] = show_user
    context['user_login'] = user_login
    # -----------------主要部分---------------------
    return render_to_response("detail.html",context)

#物品列表显示
def objList_view(request):
    #审核通过的物品,按提交时间(id)降序
    obj_db = models.Object.objects.filter(state=1).order_by('-id')
    if len(obj_db)==0:
        return HttpResponse('no valid information of objects')
    context={'context':obj_db}

    return render_to_response("objList.html",context)

# 个人中心-用户
def profile_view(request,nav_id):
    # 1.通过request.session获得登陆用户
    # 2.显示用户得个人信息
    # 3.利用"二级页面"的逻辑，显示用户发表过的信息记录
#----------------------------------------------------------------
    #处理复选框选中的物品
    if request.method == "POST":
        confirm_delete = request.POST.getlist("delete")
        confirm_finish = request.POST.getlist("finish")
        #确认按钮(删除、完成)哪一个按下,这里的完成是模态对话框中的完成
        if len(confirm_delete)>0:
            check_box_list = request.POST.getlist("object")
            for obj_id in check_box_list:
                models.Object.objects.get(id=str(obj_id)).delete()
        elif len(confirm_finish)>0:
            #修改taken表和object表
            another_id = request.POST.get("finish_id")
            check_box_list = request.POST.getlist("object")
            for obj_id in check_box_list:
                #更改物品状态
                p=models.Object.objects.get(id=str(obj_id))
                if p.state == 0 or p.state == -1:
                    continue
                p.state=2
                p.save()
                #创建Taken表记录
                try:
                    takenrecord = models.TakenRecord()
                    user1 = models.User.objects.get(sno=request.session["sno"])
                    user2 = models.User.objects.get(sno=another_id)
                    obj = models.Object.objects.get(id=obj_id)
                    takenrecord.user1 = user1
                    takenrecord.user2 = user2
                    takenrecord.object = obj
                    if obj.tag:#招领物品
                        takenrecord.tag = False #用户2来认领
                    else:
                        takenrecord.tag = True #用户2提供失物
                    takenrecord.save()
                except models.User.DoesNotExist:
                    return HttpResponse("The user (id="+another_id+") doesn't exist in database.")


#----------------------------------------------------------------
    context = {}  # form字典
    try:
        sno_login = request.session["sno"]
    except KeyError:
        # 未登录的情况下，使用session会报错：KeyError
        return render_to_response("personal.html", context)
    # 已登录
    try:
        # step1
        user_login = models.User.objects.get(sno=sno_login)
        context["user"] = user_login  # 将'用户'加入字典中
        # step2
        userobject_db = models.UserObject.objects.filter(user=user_login)
        lostobjs = []
        foundobjs = []
        for item in userobject_db:
            if item.object.tag==False:
                lostobjs.append(item.object)
            elif item.object.tag==True:
                foundobjs.append(item.object)
            # 将所有用户的物品记录放到objs中
        if len(lostobjs) == 0:
            context["lost_no_history"] = True
        else:
            context["lostobjs"] = lostobjs
        if len(foundobjs) == 0:
            context["found_no_history"] = True
        else:
            context["foundobjs"] = foundobjs  # 将'记录'加入字典字典
#-------------------------------------------------------------------
        context["nav_id"]=nav_id #导航栏序号
        # step for review 审核功能
        obj_review = models.Object.objects.filter(state=0)
        if len(obj_review)==0:
            context["review_no_history"] = True
        else:
            context["obj_review"]=obj_review
#-------------------------------------------------------------------
    except models.User.DoesNotExist:
            # 数据库没有该用户
        return HttpResponse("The user (id="+request.session["sno"]+") doesn't exist in database.")
    return render_to_response("personal.html", context)

# 退出按钮
def quit_view(request):
    # 1.清除用户登陆，包括cookie
    # 2.退出后，跳转到主界面（现在先跳转到登陆界面
    del request.session['sno']
    return redirect("/main")

# 主界面
def main_view(request):
    context={}
    # 选择最近的【失物招领】和【寻物启事】各8条
    try:
        lost_db = models.Object.objects.filter(tag=False)
        found_db = models.Object.objects.filter(tag=True)
        # 首页每个部分最多显示8个物品
        if len(lost_db)>8:
            num_lost = 8
        else:
            num_lost = len(lost_db)
        if len(found_db)>8:
            num_found = 8
        else:
            num_found = len(found_db)

        lost=[]
        found=[]

        # 将经过审核的物品信息显示
        if num_lost!=0:
            for obj in lost_db:
                if obj.state==1:# state=1表示审核过，未完成
                    lost.append(obj)
                    num_lost=num_lost-1
                if num_lost==0:
                    break
        if num_found!=0:
            for obj in found_db:
                if obj.state==1:# state=1表示审核过，未完成
                    found.append(obj)
                    num_found=num_found-1
                if num_found==0:
                    break

    except models.Object.DoesNotExist:
        return HttpResponse("DoesNotExist Error")

    context['lost']=lost
    context['found']=found

    if 'sno' in request.session:
        # 用户已登陆
        user_login = models.User.objects.get(sno=request.session['sno'])
        context['user_sno']=user_login.sno
        context['user_name']=user_login.name
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
        context["no_history"] = True
    except models.AllSort.DoesNotExist:
        HttpResponse("models.AllSort.DoesNotExist")

    objs_lost = []
    objs_found = []
    for item in sortobj_db:
        # step2
        if item.object.state>0: # 筛选通过审核的
            if item.object.tag == False:
                objs_lost.append(item.object) # 将所有用户的物品记录放到objs_lost(寻物表)中
            else:# tag=True
                objs_found.append(item.object) # 将所有用户的物品记录放到objs_found(失物表)中

    if len(objs_lost) == 0:
        context["no_lost"] = True
    else:
        context["objs_lost"] = objs_lost  # 将'记录'加入字典字典
    if len(objs_found) == 0:
        context["no_found"] = True
    else:
        context["objs_found"] = objs_found  # 将'记录'加入字典字典

    # 用于导航栏显示用户
    if 'sno' in request.session:
        # 用户已登陆
        user_login = models.User.objects.get(sno=request.session['sno'])
        context['user_sno']=user_login.sno
        context['user_name']=user_login.name
    return render_to_response('second.html',context)


#完善用户信息,当用户使用初始密码登陆后需要修改密码及完善个人信息
def complete_view(request):
    context = {}
    try:
        sno_login = request.session["sno"]
    except KeyError:
    # 未登录的情况下，使用session会报错：KeyError
        return redirect('/main')
    if request.method == 'GET':
        # 已登录
        form = forms.complete_form()
        context["form"] = form 
        context["user"] = sno_login
        return render_to_response("complete_info.html",context)
    else:
        form = forms.complete_form(request.POST)
        if form.is_valid():
            context["user"] = sno_login
            context["form"] = form
            user = models.User.objects.get(sno=sno_login)
            newpwd1 = form.cleaned_data['pwd1']
            newpwd2 = form.cleaned_data['pwd2']
            if newpwd1 == user.pwd or newpwd1 != newpwd2:#前后两次输入密码不同或者输入密码与原密码相同
                context['password_wrong']=True
                return render_to_response('complete_info.html',context)
            user.pwd = newpwd1
            user.name = form.cleaned_data['name']
            user.phone = form.cleaned_data['phone']
            user.email = form.cleaned_data['email']
            user.save()
            return redirect('/main')
        else:
            context["form"] = form
            context["user"] = sno_login
            return render_to_response('complete_info.html',context)

