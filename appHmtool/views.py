from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from pyexcel_xlsx import get_data as xlsx_get
from appHmtool.models import Transactions
import datetime
from django.db.models import F, Func, Value, CharField, Count, Sum
from django.db.models.functions import TruncMonth, TruncDate


# Create your views here.
# def home(request):
#     return render(request, 'home.html')

class home(APIView):
    def post(self, request):
        file = self.request.FILES.get('host_excel')

        try:
            data = xlsx_get(file, column_limit=19).get('SheetJS')[1:]
            date = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            upload_id = [datetime.datetime.now().strftime("%Y%m%d%H%M%S")]
            # upload_id = ['20210715122958']

            Transactions.objects.all().delete()
            for row in data:
                
                
                data_list = date + row[:13] + row[-1:] + upload_id
                
                if data_list[3] == 'already_delivery':
                    dic = {'upload_time': data_list[0], 'sale_warehouse': data_list[1], 'sale_id': data_list[2],
                           'sale_status': data_list[3], 'sale_updated_time': data_list[4], 'sale_client': data_list[5],
                           'sale_name': data_list[6], 'product_barcode': data_list[7], 'product_name_cn': data_list[8],
                           'product_name_en': data_list[9], 'product_brand': data_list[10],
                           'product_supplier': data_list[11],
                           'sale_quantity': data_list[12], 'sale_price': data_list[13], 'sale_payment': data_list[14],
                           'upload_id': data_list[15]}
                    Transactions.objects.create(**dic)

            product_brand = Transactions.objects.values('product_brand').first()['product_brand']

            response = {}
            years = []
            response['product_brand'] = product_brand

            month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            year_list = list(Transactions.objects.filter(upload_id=upload_id[0]).values(
                'sale_updated_time__year').distinct().order_by('-sale_updated_time__year'))
            for i in year_list:
                year = i['sale_updated_time__year']
                years.append(year)

                total_quantity_by_month = Transactions.objects.filter(upload_id=upload_id[0]).filter(
                    sale_updated_time__year=year).annotate(month=TruncMonth('sale_updated_time')).values(
                    'month').annotate(s=Sum('sale_quantity')).order_by().values_list('month', 's').order_by('month')
                total_payment_by_month = Transactions.objects.filter(upload_id=upload_id[0]).filter(
                    sale_updated_time__year=year).annotate(month=TruncMonth('sale_updated_time')).values(
                    'month').annotate(s=Sum('sale_payment')).order_by().values_list('month', 's').order_by('month')

                total_quantity_by_month_list = [0] * 12
                total_payment_by_month_list = [0] * 12
                for i in total_quantity_by_month:
                    total_quantity_by_month_list[(i[0].month - 1)] = float(i[1])
                for i in total_payment_by_month:
                    total_payment_by_month_list[(i[0].month - 1)] = float(round(i[1], 4))

                # V1. List
                # this_year['total'] = total
                # this_year['total_quantity_by_month_list'] = total_quantity_by_month_list
                # this_year['total_payment_by_month_list'] = total_payment_by_month_list

                # V2. JSON
                # this_year = {}
                # total_q = {}
                # total_p = {}
                # total_q[str(year)+'年'] ='总数量'
                # total_p[str(year)+'年'] ='总金额'
                # for i in range(12):
                #     total_q[month[i]] =  total_quantity_by_month_list[i]
                #     total_p[month[i]] =  total_payment_by_month_list[i]
                # this_year['total'] = [total_q,total_p]

                this_year = {}
                new_list = []
                new_list.append([str(year) + '年'] + month + ['总量'])
                new_list.append(['销售数量'] + total_quantity_by_month_list + [sum(total_quantity_by_month_list)])
                new_list.append(['销售金额'] + total_payment_by_month_list + [sum(total_payment_by_month_list)])
                this_year['total'] = new_list

                # sale_client_list = list(Transactions.objects.filter(upload_id = upload_id[0]).values('sale_client').distinct().order_by('-sale_client'))
                sale_client_list_order_q = list(
                    Transactions.objects.filter(sale_updated_time__year=year).filter(upload_id=upload_id[0]).values(
                        'sale_client').annotate(s=Sum('sale_quantity')).order_by('-s'))
                sale_client_list_order_p = list(
                    Transactions.objects.filter(sale_updated_time__year=year).filter(upload_id=upload_id[0]).values(
                        'sale_client').annotate(s=Sum('sale_payment')).order_by('-s'))

                new_list_q = []
                new_list_p = []
                new_list_q.append(['渠道'] + month + ['总数'])
                new_list_p.append(['渠道'] + month + ['总额'])

                for i in sale_client_list_order_q:
                    client = i['sale_client']
                    client_quantity_by_month = Transactions.objects.filter(sale_updated_time__year=year).filter(
                        upload_id=upload_id[0]).filter(sale_client=client).annotate(
                        month=TruncMonth('sale_updated_time')).values('month').annotate(
                        s=Sum('sale_quantity')).order_by().values_list('month', 's').order_by('month')
                    client_quantity_by_month_list = [0] * 12
                    for i in client_quantity_by_month:
                        client_quantity_by_month_list[(i[0].month - 1)] = float(i[1])
                    new_list_q.append(
                        [client] + client_quantity_by_month_list + [sum(client_quantity_by_month_list)])

                for i in sale_client_list_order_p:
                    client = i['sale_client']
                    client_payment_by_month = Transactions.objects.filter(sale_updated_time__year=year).filter(
                        upload_id=upload_id[0]).filter(sale_client=client).annotate(
                        month=TruncMonth('sale_updated_time')).values('month').annotate(
                        s=Sum('sale_payment')).order_by().values_list('month', 's').order_by('month')
                    client_payment_by_month_list = [0] * 12
                    for i in client_payment_by_month:
                        client_payment_by_month_list[(i[0].month - 1)] = float(round(i[1], 4))
                    new_list_p.append([client] + client_payment_by_month_list + [sum(client_payment_by_month_list)])

                this_year['by_client_quantity'] = new_list_q
                this_year['by_client_payment'] = new_list_p

                new_list_q = []
                new_list_p = []
                new_list_q.append(['产品条码'] + ['产品英文名'] + ['产品中文名'] + month + ['总数'])
                new_list_p.append(['产品条码'] + ['产品英文名'] + ['产品中文名'] + month + ['总额'])
                # sale_product_list = list(Transactions.objects.filter(upload_id = upload_id[0]).values('product_barcode').distinct().order_by('product_barcode'))

                sale_product_list_order_q = list(
                    Transactions.objects.filter(sale_updated_time__year=year).filter(upload_id=upload_id[0]).values(
                        'product_barcode').annotate(s=Sum('sale_quantity')).order_by('-s'))
                sale_product_list_order_p = list(
                    Transactions.objects.filter(sale_updated_time__year=year).filter(upload_id=upload_id[0]).values(
                        'product_barcode').annotate(s=Sum('sale_payment')).order_by('-s'))

                for i in sale_product_list_order_q:
                    product = i['product_barcode']
                    name_cn = \
                    Transactions.objects.filter(upload_id=upload_id[0]).filter(product_barcode=product).values(
                        'product_name_cn').first()['product_name_cn']
                    name_en = \
                    Transactions.objects.filter(upload_id=upload_id[0]).filter(product_barcode=product).values(
                        'product_name_en').first()['product_name_en']
                    product_quantity_by_month = Transactions.objects.filter(sale_updated_time__year=year).filter(
                        upload_id=upload_id[0]).filter(product_barcode=product).annotate(
                        month=TruncMonth('sale_updated_time')).values('month').annotate(
                        s=Sum('sale_quantity')).order_by().values_list('month', 's').order_by('month')
                    product_quantity_by_month_list = [0] * 12

                    for i in product_quantity_by_month:
                        product_quantity_by_month_list[(i[0].month - 1)] = float(i[1])

                    new_list_q.append([product] + [name_en] + [name_cn] + product_quantity_by_month_list + [
                        sum(product_quantity_by_month_list)])

                for i in sale_product_list_order_p:
                    product = i['product_barcode']
                    name_cn = \
                    Transactions.objects.filter(upload_id=upload_id[0]).filter(product_barcode=product).values(
                        'product_name_cn').first()['product_name_cn']
                    name_en = \
                    Transactions.objects.filter(upload_id=upload_id[0]).filter(product_barcode=product).values(
                        'product_name_en').first()['product_name_en']
                    product_payment_by_month = Transactions.objects.filter(sale_updated_time__year=year).filter(
                        upload_id=upload_id[0]).filter(product_barcode=product).annotate(
                        month=TruncMonth('sale_updated_time')).values('month').annotate(
                        s=Sum('sale_payment')).order_by().values_list('month', 's').order_by('month')
                    product_payment_by_month_list = [0] * 12

                    for i in product_payment_by_month:
                        product_payment_by_month_list[(i[0].month - 1)] = float(round(i[1], 4))

                    new_list_p.append([product] + [name_en] + [name_cn] + product_payment_by_month_list + [
                        sum(product_payment_by_month_list)])

                this_year['by_product_quantity'] = new_list_q
                this_year['by_product_payment'] = new_list_p

                response[year] = this_year

            response['year_list'] = years

            # print(list(year_list))
            # print(list(count))
            # response['count'] = list(count)

            return JsonResponse(response)


        except Exception as e:
            return HttpResponse(e)

    def get(self, request):
        return render(request, 'hmtool/home.html')