from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from pyexcel_xlsx import get_data as xlsx_get
from appHmtool.models import Transactions
import datetime
from django.db.models import F, Func, Value, CharField, Count, Sum
from django.db.models.functions import TruncMonth, TruncDate
import pandas as pd



# Create your views here.

class home(APIView):
    def post(self, request):
        
        file = self.request.FILES.get('host_excel')

        try:
            df = pd.read_excel(file,dtype=object)
            df = df.loc[df['订单状态'] == 'already_delivery']
            df = df[df['更新时间'].notnull()]
            df['客户名字'] = df['客户名字'].replace(['Xpanda Go', 'ACI Holdings Pty Ltd'], 'XPG')
            df['year'] = pd.DatetimeIndex(df['更新时间']).year
            df['month'] = pd.DatetimeIndex(df['更新时间']).month
            df['month_year'] = pd.to_datetime(df['更新时间']).dt.to_period('M').astype(str)
            # df['month_year'] = str(int(df['year'])) + str(int(df['month']))

            month_year = list(df['month_year'].unique())
            month_year.reverse()

  


            if len(month_year) > 12:
                return HttpResponse('文件数据时间段超过12个月 请上传12个月区间的数据')
            else:
                n = 12 - len(month_year)
                month = month_year + [' ']*n

            month_index = {}

            i = 0 
            for item in month:
                month_index[item] = i
                i += 1

            


            # month = []
            # count = 0
            # for i in month_year:
            #     month.append(i)

    
            

            # years = list(df['year'].unique())
            product_brand = list(df['品牌'].unique())[0]
            upload_id = [datetime.datetime.now().strftime("%Y%m%d%H%M%S")]

            response = {}
            response['product_brand'] = product_brand
            response['upload_id'] = upload_id[0]

            year_list = []
            year = month_year[0] + '至' + month_year[-1]
            year_list.append(year)
            

            # for i in years:
            #     year_list.append(int(i))
            # response['year_list'] = year_list
            # year = year_list[0]

            # for year in year_list:
            # month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            total_quantity_by_month = df.groupby('month_year').agg({'数量':['sum']})
            total_payment_by_month = df.groupby('month_year').agg({'货款合计':['sum']})
            sale_client_list_order_q = df.groupby('客户名字').agg({'数量':['sum']}).sort_values(by=('数量', 'sum'),ascending=False)
            sale_client_list_order_p = df.groupby('客户名字').agg({'货款合计':['sum']}).sort_values(by=('货款合计', 'sum'),ascending=False)
            sale_product_list_order_q = df.groupby(['货品编号','品名(中文)','品名(英文)']).agg({'数量':['sum']}).sort_values(by=('数量', 'sum'),ascending=False)
            sale_product_list_order_p = df.groupby(['货品编号','品名(中文)','品名(英文)']).agg({'货款合计':['sum']}).sort_values(by=('货款合计', 'sum'),ascending=False)

            total_quantity_by_month_list = [' '] * 12
            total_payment_by_month_list = [' '] * 12



            

            
            for index, row in total_quantity_by_month.iterrows():
                total_quantity_by_month_list[month_index[index]] = int(row.values[0])
            for index, row in total_payment_by_month.iterrows():
                total_payment_by_month_list[month_index[index]] = round(float(row.values[0]),2)

   
      


            this_year = {}
            new_list = []
            new_list.append(['销售时间'] + month + ['总量'])
            new_list.append(['销售数量'] + total_quantity_by_month_list + [round(sum(filter(lambda i: isinstance(i, int), total_quantity_by_month_list)),2)])
            new_list.append(['销售金额'] + total_payment_by_month_list + [round(sum(filter(lambda i: isinstance(i, float), total_payment_by_month_list)),2)])
            this_year['total'] = new_list

            new_list_q = []
            new_list_p = []
            new_list_q.append(['渠道'] + month + ['总数'])
            new_list_p.append(['渠道'] + month + ['总额'])

           

            for index, row in sale_client_list_order_q.iterrows():
                client = index
                client_quantity_by_month = df.loc[(df['客户名字'] == client)].groupby('month_year').agg({'数量':['sum']})
                client_quantity_by_month_list = [''] * 12
                for index, row in client_quantity_by_month.iterrows():
                    client_quantity_by_month_list[month_index[index]] = int(row.values[0])
                new_list_q.append([client] + client_quantity_by_month_list + [round(sum(filter(lambda i: isinstance(i, int), client_quantity_by_month_list)),2)])
            for index, row in sale_client_list_order_p.iterrows():
                client = index
                client_payment_by_month = df.loc[(df['客户名字'] == client)].groupby('month_year').agg({'货款合计':['sum']})
                client_payment_by_month_list = [''] * 12
                for index, row in client_payment_by_month.iterrows():
                    client_payment_by_month_list[month_index[index]] = round(float(row.values[0]),2)
                new_list_p.append([client] + client_payment_by_month_list + [round(sum(filter(lambda i: isinstance(i, float), client_payment_by_month_list)),2)])
            
            this_year['by_client_quantity'] = new_list_q
            this_year['by_client_payment'] = new_list_p


            new_list_q = []
            new_list_p = []
            new_list_q.append(['产品条码'] + ['产品英文名'] + ['产品中文名'] + month + ['总数'])
            new_list_p.append(['产品条码'] + ['产品英文名'] + ['产品中文名'] + month + ['总额'])
        
            for index, row in sale_product_list_order_q.iterrows():
                product = index[0]
                name_cn = index[1]
                name_en = index[2]
                product_quantity_by_month = df.loc[(df['货品编号'] == product)].groupby('month_year').agg({'数量':['sum']})
                product_quantity_by_month_list = [' '] * 12
                for index, row in product_quantity_by_month.iterrows():
                    product_quantity_by_month_list[month_index[index]] = int(row.values[0])
                new_list_q.append([product] + [name_en] + [name_cn] + product_quantity_by_month_list + [round(sum(filter(lambda i: isinstance(i, int), product_quantity_by_month_list)),2)])
            for index, row in sale_product_list_order_p.iterrows():
                product = index[0]
                name_cn = index[1]
                name_en = index[2]
                product_payment_by_month = df.loc[(df['货品编号'] == product)].groupby('month_year').agg({'货款合计':['sum']})
                product_payment_by_month_list = [' '] * 12
                for index, row in product_payment_by_month.iterrows():
                    product_payment_by_month_list[month_index[index]] = round(float(row.values[0]),2)
                new_list_p.append([product] + [name_en] + [name_cn] + product_payment_by_month_list + [round(sum(filter(lambda i: isinstance(i, float), product_payment_by_month_list)),2)])
            
            
            this_year['by_product_quantity'] = new_list_q
            this_year['by_product_payment'] = new_list_p
            



            this_client = {}
            for index, row in sale_client_list_order_p.iterrows():
                client = index
                client_list_q = []   
                client_list_q.append(['产品条码'] + ['产品英文名'] + ['产品中文名'] + month + ['总数'] + ['总金额'])
                client_product_quantity_order = df[df['客户名字'].isin([client])].groupby(['货品编号','品名(中文)','品名(英文)']).agg({'数量':['sum']}).sort_values(by=('数量', 'sum'),ascending=False)
                for index, row in client_product_quantity_order.iterrows():
                    
                    product = index[0]
                    name_cn = index[1]
                    name_en = index[2]
                    client_product_quantity_by_month = df.loc[(df['货品编号'] == product)][df.loc[(df['货品编号'] == product)]['客户名字'].isin([client])].groupby('month_year').agg({'数量':['sum']})
                    client_product_quantity_by_month_list = [' '] * 12
                    for index, row in client_product_quantity_by_month.iterrows():
                        client_product_quantity_by_month_list[month_index[index]] = int(row.values[0])
                    client_payment = round(float(df.loc[(df['货品编号'] == product)][df.loc[(df['货品编号'] == product)]['客户名字'].isin([client])].agg({'货款合计':['sum']}).values[0]),2)

                    client_list_q.append([product] + [name_en] + [name_cn] + client_product_quantity_by_month_list + [round(sum(filter(lambda i: isinstance(i, int), client_product_quantity_by_month_list)),2)] + [client_payment])
                this_client[client] = client_list_q
            this_year['pptx'] = this_client
            this_year['pptx_list'] = sale_client_list_order_p.index.tolist()

        
    




            response[year] = this_year
            response['year_list'] = year_list

            
            
            return JsonResponse(response)
        except Exception as e:
            return HttpResponse(e)

    def get(self, request):
        return render(request, 'hmtool/home.html')
 
