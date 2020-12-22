from django.shortcuts import render, HttpResponse, redirect
from django.db.models.functions import TruncMonth, TruncDate
from django.db.models import F, Func, Value, CharField, Count, Sum
from dash.models import delivery, material
# Create your views here.
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.forms import Form, fields, widgets
from django.utils.dateparse import parse_date
from django.template.loader import render_to_string
import json

class Round2(Func):
    function ="ROUND"
    template ="%(function)s(%(expressions)s::numeric, 2)"

def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        user = request.POST.get('username')
        pwd = request.POST.get('password')
        if user == 'admin' and pwd == '123':
            request.session['user'] = 'admin'
            return redirect('/dashMain')
        else:
            return render(request,'login.html')
        
def dashMain(request):
        if request.method == "POST":
            
#            ret = {'status': True, 'messege': None}
            start = parse_date(request.POST.get('startDate'))
            end = parse_date(request.POST.get('endDate'))
            diff = end - start
            if diff.days < 7:
                start_two = start - timedelta(days=6)
                end = end + timedelta(days=1)
                receiveN = delivery.objects.filter(uploadTime__gte = start_two).filter(uploadTime__lte = end).annotate(uploadDate=TruncDate('uploadTime')).values('uploadDate').annotate(c=Count('id')).values('uploadDate','c').order_by('-uploadDate')
                recentT = delivery.objects.filter(uploadTime__lte = end).order_by('-uploadTime')[:5]
            else:
                end = end + timedelta(days=1)
                receiveN = delivery.objects.filter(uploadTime__gte = start).filter(uploadTime__lte = end).annotate(uploadDate=TruncDate('uploadTime')).values('uploadDate').annotate(c=Count('id')).values('uploadDate','c').order_by('-uploadDate')
                recentT = delivery.objects.filter(uploadTime__gte = start).filter(uploadTime__lte = end).order_by('-uploadTime')[:5]
            ctgStat = delivery.objects.filter(uploadTime__gte = start).filter(uploadTime__lte = end).values('category__mainCategory').annotate(t=Round2(Sum('quantity'))).order_by('-t')  
#            print(ctgStat)
            sCtgStat = delivery.objects.filter(uploadTime__gte = start).filter(uploadTime__lte = end).values('category__categoryName').annotate(t=Round2(Sum('quantity'))).order_by('-t')[:10]
            totalR = delivery.objects.filter(uploadTime__gte = start).filter(uploadTime__lte = end).count()
            totalQ = delivery.objects.filter(uploadTime__gte = start).filter(uploadTime__lte = end).aggregate(Sum('quantity'))   
            recent_list = recentT.values("id","project","location","driverName","plateNumber","receiverName","receiveID","quantity","unit","date","time","uploadTime","category_id","category__categoryName")
            context = {'recent': recent_list}
            recentTable = {'recentTable': render_to_string('dash/recentTable.html', context=context)}
            activeP = delivery.objects.filter(uploadTime__gte = start).filter(uploadTime__lte = end).values('project').annotate(c=Count('id')).values('project','c').order_by('-c').first()
            return JsonResponse({"receiveN": list(receiveN),'ctgStat':list(ctgStat),'sCtgStat':list(sCtgStat),'recentT': recentTable,'totalQ':totalQ,'totalR':totalR,'activeP':activeP})
        else:
            return render(request, 'dash/dashMain.html')
    
def dataTable(request):
    if request.method == "POST":
#            ret = {'status': True, 'messege': None}
#            timeRange = int(request.POST.get('timeRange'))  
        start = parse_date(request.POST.get('startDate'))
        end = parse_date(request.POST.get('endDate'))

#        print(start,end)
        if start == end :  
            end = end + timedelta(days=1)
            data = delivery.objects.filter(uploadTime__gte = start).filter(uploadTime__lte = end).order_by('-uploadTime')
        else:
            end = end + timedelta(days=1)
            data = delivery.objects.filter(uploadTime__gte = start).filter(uploadTime__lte = end).order_by('-uploadTime')
        data_list = data.values()
        data_list2 = data.values("id","project","location","driverName","plateNumber","receiverName",    "receiveID","quantity","unit","uploadTime","category_id","category__categoryName")
        return JsonResponse({"newData": list(data_list2)})
    else:    
        obj = dataForm()
        return render(request, 'dash/dataTable.html',{'obj':obj})
    
def mngTemp(request):
    mc = material.objects.values('mainCategory').distinct()
    m = material.objects.all().order_by('id')
    return render(request, 'dash/mngTemp.html',{'mc':mc,'m':m})

#def lookUp(request):
#    v = request.session.get('user')
#    if not v:
#        return redirect('/login/')
#    else:
#        return render(request, 'lookUp.html')
    

    
class dataForm(Form):

    driverName = fields.CharField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    date = fields.DateField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    location = fields.CharField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    plateNumber = fields.CharField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    project = fields.CharField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    quantity = fields.FloatField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null",'invalid':'must be number'})
    receiveID = fields.CharField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    receiverName = fields.CharField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    category_id = fields.IntegerField( 
    )
    time = fields.TimeField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    unit = fields.CharField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    uploadTime = fields.DateTimeField(widget=widgets.TextInput(attrs={'class':'form-control'}),error_messages={'required': "can't be null"})
    def __init__(self, *args, **kwargs):  # 自定义__init__
        super(dataForm, self).__init__(*args, **kwargs) 
        self.fields['category_id'].widget = widgets.Select(choices=material.objects.values_list('id','categoryName'), attrs={'class':'form-control'})    



def ajax_addData(request):
    ret = {'status':True,'msg':None}
    obj = dataForm(request.POST)
    if obj.is_valid():
        delivery.objects.create(**obj.cleaned_data)
    else:
        ret['status'] = False
        ret['msg'] = obj.errors
    v = json.dumps(ret)
    return HttpResponse(v)

def ajax_deleteData(request):
    ret = {'status':True,'msg':None}
    nid = request.POST['nid']
    delivery.objects.filter(id=nid).delete()
    v = json.dumps(ret)
    return HttpResponse(v)

def ajax_addCtg(request):
    ret = {'status':True,'msg':None}
    ctgName = request.POST['ctgName']
    mainCtg = request.POST['mainCtg']
    newid = material.objects.values('id').order_by('-id').first()['id'] + 1
    if material.objects.filter(categoryName=ctgName).exists():
        ret['status'] = False
        ret['msg'] = '重复名称，无法添加!'
    else:
        material.objects.create(id=newid,categoryName=ctgName,mainCategory=mainCtg)
    v = json.dumps(ret)
    return HttpResponse(v)

def ajax_delCtg(request):
    ret = {'status':True,'msg':None}
    nid = request.POST['nid']
    if delivery.objects.filter(category_id=nid).exists():
        ret['status'] = False
        ret['msg'] = '数据库里还有关联数据，无法删除!'
    else:
        material.objects.filter(id=nid).delete()
    v = json.dumps(ret)
    return HttpResponse(v)

def ajax_editCtg(request):
    ret = {'status':True,'msg':None}
    nid = request.POST['nid']
    name = request.POST['name']
    if material.objects.filter(categoryName=name).exists():
        ret['status'] = False
        ret['msg'] = '重复名称，无法修改!'
    else:
        material.objects.filter(id=nid).update(categoryName=name)
    v = json.dumps(ret)
    return HttpResponse(v)

def editData(request, nid):
    if request.method=="GET":
        row = delivery.objects.filter(id=nid).values().first()
        obj = dataForm(initial=row)
        return render(request,"dash/editData.html",{'nid':nid,'obj':obj})
    else:
        obj = dataForm(request.POST)
        return redirect('/dash/dataTable/')
#        if obj.is_valid():
#            delivery.objects.filter(id=nid).update(**obj.cleaned_data)
#            return redirect('/dash/dataTable/')
#        return render(request,"dash/editData.html",{'nid':nid,'obj':obj})
        

