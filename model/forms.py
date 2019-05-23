from django import forms

class login_form(forms.Form):
    username = forms.CharField(max_length=10,label="学号")
    password = forms.CharField(max_length=20,widget=forms.PasswordInput,label="密码")
    # 这里的变量名需要同html表单中的name保持一致，否则无法读入信息

class objUpload_form(forms.Form):
    # 为了适配html
    name = forms.CharField(max_length=10)       #物品名称
    time = forms.CharField(max_length=20)       #捡到/丢失时间
    position = forms.CharField(max_length=100)  #捡到丢失地点
    dscp = forms.CharField(max_length=1000,widget=forms.Textarea)   #细节描述
    img  = forms.ImageField(required=False)     #图片
    tag = forms.CharField(max_length=20)        #tag 表明是失物招领还是寻物启事
    categary = forms.CharField(max_length=20)   #物品分类

class complete_form(forms.Form):
    pwd1 = forms.CharField(
        required = True,
        label = "新密码:",
        error_messages={'required':"请输入新密码"},
        widget = forms.PasswordInput(
            attrs={
                'placeholder':"新密码",
                'class':"form-control col-sm4",
            }),
        min_length=3,
        max_length=20)                                      #第一次输入的密码
    pwd2 = forms.CharField(
        required = True,
        label = "确认密码:",
        error_messages={'required':"请再次输入新密码"},
        widget = forms.PasswordInput(
            attrs={
                'placeholder':"确认密码",
                'class':"form-control col-sm4",             #可以设置前端表单的效果
            }),
        min_length=3,
        max_length=20)                                      #第二次输入的密码
    # name = forms.CharField(
    #     required = True,
    #     label = "姓名",
    #     widget = forms.TextInput(
    #         attrs={
    #             'placeholder':"在此填写姓名",
    #             'class':"form-control col-sm4",             #可以设置前端表单的效果
    #         }),
    #     max_length=10)                                      #姓名
    phone = forms.CharField(
        required = True,
        label = "电话:",
        widget = forms.TextInput(
            attrs={
                'placeholder':"在此填写电话",
                'class':"form-control col-sm4",
            }),
        error_messages={'required':"电话长度输入有误"},
        min_length=7,
        max_length=15)                                      #电话
    email = forms.EmailField(
        required = True,
        label = "邮箱:",
        widget = forms.EmailInput(
            attrs={
                'placeholder':"在此填写邮箱",
                'class':"form-control col-sm4",
            }),
        error_messages={'required':"邮箱输入格式有误"},
        max_length=50)                                      #邮箱
    
class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    file = forms.FileField()