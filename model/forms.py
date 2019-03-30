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
