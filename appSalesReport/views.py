from django.shortcuts import render
from django.db.models.functions import TruncMonth, TruncDate
from django.db.models import F, Func, Value, CharField, Count, Sum
from appSalesReport.models import Products, Company, Transactions
from django.http import JsonResponse
import datetime
import json


def required_method(method_list):
    def _required_method_decorator(func):
        def my_function(request, *args, **kwargs):
            if request.method in method_list:
                return func(request, *args, **kwargs)
            else:
                return HttpResponse(
                    json.dumps({
                        "result": False,
                        "data": [],
                        "message": u"Please change to %s" % "、".join(method_list),
                        "code": -1
                    }), content_type='application/json')

        return my_function
    return _required_method_decorator

def sales_report(request):
    return render(request, 'sales-report/sales-report.html')

@required_method(['GET'])
def get_company(request):
    response = {}
    try:
        company = Company.objects.all().order_by('name').values()
        year_list = Transactions.objects.values('time__year').distinct().order_by('-time__year')
        response['list'] = list(company)
        response['year_list'] = list(year_list)
        response['msg'] = "success"
        response['error_num'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1

    return JsonResponse(response)

months = [1,2,3,4,5,6,7,8,9,10,11,12]
@required_method(['POST'])
def get_lineChart(request):
    company = request.POST.get('company')
    year = request.POST.get('year')
    last_year = int(year)-1
    season = request.POST.get('season')[:2]
    response = {}
    
 
    try:
        if season == 'FY':     
            month = [1,2,3,4,5,6,7,8,9,10,11,12]
            count = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).annotate(month=TruncMonth('time')).values('month').annotate(c=Count('id')).order_by().values_list('month','c').order_by('month')
            quantity = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).annotate(month=TruncMonth('time')).values('month').annotate(s=Sum('quantity')).order_by().values_list('month','s').order_by('month') 
            payment = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).annotate(month=TruncMonth('time')).values('month').annotate(s=Sum('payment')).order_by().values_list('month','s').order_by('month')
            payment = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).annotate(month=TruncMonth('time')).values('month').annotate(s=Sum('payment')).order_by().values_list('month','s').order_by('month')
            payment_last_year = Transactions.objects.filter(product__company_id = company ).filter(time__year = last_year).annotate(month=TruncMonth('time')).values('month').annotate(s=Sum('payment')).order_by().values_list('month','s').order_by('month')
            
            

            count_list = [' '] * 12
            quantity_list = [' '] * 12
            payment_list = [' '] * 12
            payment_last_year_list = [' '] * 12
            label_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            for i in count:
                count_list[(i[0].month-1)]=i[1]
            for i in quantity:
                quantity_list[(i[0].month-1)]=i[1]
            for i in payment:
                payment_list[(i[0].month-1)]=i[1]
            for i in payment_last_year:
                payment_last_year_list[(i[0].month-1)]=i[1]
        else:
            n_season = int(season[-1]) -1
            month = [1+3*n_season,2+3*n_season,3+3*n_season]
            count = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).extra({"week": "date_trunc('week', time)"}).values("week").order_by().annotate(c=Count("id")).values_list('week','c').order_by('week')
            quantity = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).extra({"week": "date_trunc('week', time)"}).values("week").order_by().annotate(s=Sum("quantity")).values_list('week','s').order_by('week')
            payment = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).extra({"week": "date_trunc('week', time)"}).values("week").order_by().annotate(s=Sum("payment")).values_list('week','s').order_by('week')    

                     
            count_list = []
            quantity_list = []
            payment_list = []
            payment_last_year_list = []
            label_list = []
            check = count[0][0] - datetime.timedelta(days=7)
            i = 0
            while i < len(count):
                check = check + datetime.timedelta(days=7)  
                check_last_year = datetime.datetime(year=check.year-1, month=check.month, day=check.day,tzinfo=check.tzinfo)
                end_last_year = check_last_year + datetime.timedelta(days=7)  
                payment_ly = Transactions.objects.filter(product__company_id = company ).filter(time__gte = check_last_year).filter(time__lte = end_last_year).aggregate(Sum('payment'))
                payment_last_year_list.append(payment_ly['payment__sum'])
                if check == count[i][0]:
                    count_list.append(count[i][1])
                    quantity_list.append(quantity[i][1])
                    payment_list.append(payment[i][1])     
                    label_list.append(count[i][0].strftime("%b-%d"))
                    i += 1
                else:
                    count_list.append(0)
                    quantity_list.append(0)
                    payment_list.append(0)
                    payment_last_year_list.append(0)
                    label_list.append(check.strftime("%b-%d"))
                    i += 0
                
        total_quantity = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).aggregate(Sum('quantity'))
        total_payment = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).aggregate(Sum('payment'))
        total_count = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).count()
        top_day = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).annotate(day=TruncDate('time')).values('day').annotate(s=Sum('payment')).order_by().values_list('day','s').order_by('-s')[0]
        
    
      
        channel_proportion = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).values('channel').annotate(s=Sum('payment')).order_by().values_list('channel','s').order_by('-s')
        product_proportion = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).values('product__name_en').annotate(s=Sum('payment')).order_by().values_list('product__name_en','s').order_by('-s')
        
        top_trans = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).values('id','product__name_en','payment','price','quantity','channel','time','t_code').order_by('-payment')[:5]
        bottom_trans = Transactions.objects.filter(product__company_id = company ).filter(time__year = year).filter(time__month__in = month).values('id','product__name_en','payment','price','quantity','channel','time','t_code').order_by('payment')[:5]
            
 
        proportion = [[],[]]
        proportion_label = [[],[]]
        
        
        i = 0
        t_cp = 0
        t_pp = 0

        for i in range(len(channel_proportion)):
            cp = int(channel_proportion[i][1]/total_payment['payment__sum']*100)
            proportion[0].append(cp)
            proportion_label[0].append(channel_proportion[i][0])
            t_cp += cp
            if i == 2:
                cp = 100 - t_cp  
                proportion[0].append(cp)
                proportion_label[0].append('others')
                break
                
        for i in range(len(product_proportion)):
            pp = int(product_proportion[i][1]/total_payment['payment__sum']*100)
            proportion[1].append(pp)
            proportion_label[1].append(product_proportion[i][0])
            t_pp += pp
            if i == 2:
                pp = 100 - t_pp  
                proportion[1].append(pp)
                proportion_label[1].append('others')
                break
                
        


            
        response['count'] = list(count_list)
        response['quantity'] = list(quantity_list)
        response['payment'] = list(payment_list)
        response['payment_last_year'] = list(payment_last_year_list)
        response['label'] = list(label_list)
        
        
        response['proportion'] = list(proportion)
        response['proportion_label'] = list(proportion_label)
        
        response['total_count'] = total_count
        response['total_quantity'] = total_quantity['quantity__sum']
        response['total_payment'] = total_payment['payment__sum']
        response['top_day'] = top_day[0].strftime('%Y-%m-%d')
        response['top_day_payments'] = top_day[1]
        
        response['top_trans'] = list(top_trans)
        response['bottom_trans'] = list(bottom_trans)
        
        
        response['msg'] = "success"
        response['error_num'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1
        

    return JsonResponse(response)