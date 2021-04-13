from django.shortcuts import render
from covidDash.models import covid
from django.http import JsonResponse
from datetime import datetime,timedelta

import json

import time


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
                        "message": u"请使用%s方法" % "、".join(method_list),
                        "code": -1
                    }), content_type='application/json')

        return my_function
    return _required_method_decorator
# Create your views here.
def covidDash(request):
    return render(request, 'covid-dash/covidDash.html')

tab_list = [50,100,99999]

@required_method(['POST'])
def get_data(request):
#    company = 7
    tab = int(request.POST.get('tab'))
#    last_year = int(year)-1
#    season = request.POST.get('season')[:2]
    today = datetime.today().strftime('%Y-%m-%d')
    d_month = (datetime.today() - timedelta(days=tab_list[tab-1])).strftime('%Y-%m-%d')
    lineChart = covid.objects.filter(date__gte = d_month).order_by('date').values_list('total_cases',flat=True)
    dateLabel = covid.objects.filter(date__gte = d_month).order_by('date').values_list('date',flat=True)
    barChart = {}
    barChart['new_cases'] = list(covid.objects.filter(date__gte = d_month).order_by('date').values_list('new_cases',flat=True))
    barChart['new_cases_smoothed'] = list(covid.objects.filter(date__gte = d_month).order_by('date').values_list('new_cases_smoothed',flat=True))
    
    barChart_death = {}
    barChart_death['new_deaths'] = list(covid.objects.filter(date__gte = d_month).order_by('date').values_list('new_deaths',flat=True))
    barChart_death['new_deaths_smoothed'] = list(covid.objects.filter(date__gte = d_month).order_by('date').values_list('new_deaths_smoothed',flat=True))
    
    response = {}
    try:
        response['date'] = list(dateLabel)
        response['lineChart'] = list(lineChart)
        response['barChart'] = barChart
        response['barChart_death'] = barChart_death
        
        response['error_num'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1
#    time.sleep(1)
    return JsonResponse(response)