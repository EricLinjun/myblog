from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from pyexcel_xlsx import get_data as xlsx_get
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
            df = df.loc[df['status'] == 'deliveried']
            df = df[df['date'].notnull()]
            df['year'] = pd.DatetimeIndex(df['date']).year
            df['month'] = pd.DatetimeIndex(df['date']).month
            years = list(df['year'].unique())
            product_brand = list(df['brand'].unique())[0]
            upload_id = [datetime.datetime.now().strftime("%Y%m%d%H%M%S")]

            response = {}
            response['product_brand'] = product_brand
            response['upload_id'] = upload_id[0]

            year_list = []
            for i in years:
                year_list.append(int(i))
            response['year_list'] = year_list

            for year in year_list:
                month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

                total_quantity_by_month = df.loc[df['year'] == year].groupby('month').agg({'quantity':['sum']})
                total_payment_by_month = df.loc[df['year'] == year].groupby('month').agg({'payment':['sum']})
                sale_client_list_order_q = df.loc[df['year'] == year].groupby('channel').agg({'quantity':['sum']}).sort_values(by=('quantity', 'sum'),ascending=False)
                sale_client_list_order_p = df.loc[df['year'] == year].groupby('channel').agg({'payment':['sum']}).sort_values(by=('payment', 'sum'),ascending=False)
                sale_product_list_order_q = df.loc[df['year'] == year].groupby(['barcode','name_cn','name_en']).agg({'quantity':['sum']}).sort_values(by=('quantity', 'sum'),ascending=False)
                sale_product_list_order_p = df.loc[df['year'] == year].groupby(['barcode','name_cn','name_en']).agg({'payment':['sum']}).sort_values(by=('payment', 'sum'),ascending=False)

                total_quantity_by_month_list = [0] * 12
                total_payment_by_month_list = [0] * 12
                for index, row in total_quantity_by_month.iterrows():
                    total_quantity_by_month_list[(index - 1)] = int(row.values[0])
                for index, row in total_payment_by_month.iterrows():
                    total_payment_by_month_list[(index - 1)] = round(float(row.values[0]),2)

                this_year = {}
                new_list = []
                new_list.append([str(year)] + month + ['Total'])
                new_list.append(['Volume'] + total_quantity_by_month_list + [round(sum(total_quantity_by_month_list),2)])
                new_list.append(['Sales'] + total_payment_by_month_list + [round(sum(total_payment_by_month_list),2)])
                this_year['total'] = new_list

                new_list_q = []
                new_list_p = []
                new_list_q.append(['Channel'] + month + ['Volume'])
                new_list_p.append(['Channel'] + month + ['Sales'])

                for index, row in sale_client_list_order_q.iterrows():
                    client = index
                    client_quantity_by_month = df.loc[(df['year'] == year) & (df['channel'] == client)].groupby('month').agg({'quantity':['sum']})
                    client_quantity_by_month_list = [0] * 12
                    for index, row in client_quantity_by_month.iterrows():
                        client_quantity_by_month_list[(index - 1)] = int(row.values[0])
                    new_list_q.append([client] + client_quantity_by_month_list +  [sum(client_quantity_by_month_list)])
                for index, row in sale_client_list_order_p.iterrows():
                    client = index
                    client_payment_by_month = df.loc[(df['year'] == year) & (df['channel'] == client)].groupby('month').agg({'payment':['sum']})
                    client_payment_by_month_list = [0] * 12
                    for index, row in client_payment_by_month.iterrows():
                        client_payment_by_month_list[(index - 1)] = round(float(row.values[0]),2)
                    new_list_p.append([client] + client_payment_by_month_list +  [sum(client_payment_by_month_list)])
                
                this_year['by_client_quantity'] = new_list_q
                this_year['by_client_payment'] = new_list_p


                new_list_q = []
                new_list_p = []
                new_list_q.append(['Barcode'] + ['Name_EN'] + ['Name_CN'] + month + ['Volume'])
                new_list_p.append(['Barcode'] + ['Name_EN'] + ['Name_CN'] + month + ['Sales'])
                for index, row in sale_product_list_order_q.iterrows():
                    product = index[0]
                    name_cn = index[1]
                    name_en = index[2]
                    product_quantity_by_month = df.loc[(df['year'] == year) & (df['barcode'] == product)].groupby('month').agg({'quantity':['sum']})
                    product_quantity_by_month_list = [0] * 12
                    for index, row in product_quantity_by_month.iterrows():
                        product_quantity_by_month_list[(index - 1)] = int(row.values[0])
                    new_list_q.append([product] + [name_en] + [name_cn] + product_quantity_by_month_list + [sum(product_quantity_by_month_list)])
                for index, row in sale_product_list_order_p.iterrows():
                    product = index[0]
                    name_cn = index[1]
                    name_en = index[2]
                    product_payment_by_month = df.loc[(df['year'] == year) & (df['barcode'] == product)].groupby('month').agg({'payment':['sum']})
                    product_payment_by_month_list = [0] * 12
                    for index, row in product_payment_by_month.iterrows():
                        product_payment_by_month_list[(index - 1)] = round(float(row.values[0]),2)
                    new_list_p.append([product] + [name_en] + [name_cn] + product_payment_by_month_list + [sum(product_payment_by_month_list)])
                
                
                this_year['by_product_quantity'] = new_list_q
                this_year['by_product_payment'] = new_list_p
                


                # client_quantity = df.loc[(df['year'] == year) & (df['channel'] == 'XPG')].agg({'quantity':['sum']})
                # client_payment = df.loc[(df['year'] == year) & (df['channel'] == 'XPG')].agg({'payment':['sum']})

    
                this_client = {}
                for index, row in sale_client_list_order_p.iterrows():
                    client = index
                    client_list_q = []   
                    client_list_q.append(['barcode'] + ['name_en'] + ['name_cn'] + month + ['Volume'] + ['Sales'])
                    client_product_quantity_order = df.loc[df['year'] == year][df.loc[df['year'] == year]['channel'].isin([client])].groupby(['barcode','name_cn','name_en']).agg({'quantity':['sum']}).sort_values(by=('quantity', 'sum'),ascending=False)
                    for index, row in client_product_quantity_order.iterrows():
                        
                        product = index[0]
                        name_cn = index[1]
                        name_en = index[2]
                        client_product_quantity_by_month = df.loc[(df['year'] == year) & (df['barcode'] == product)][df.loc[(df['year'] == year) & (df['barcode'] == product)]['channel'].isin([client])].groupby('month').agg({'quantity':['sum']})
                        client_product_quantity_by_month_list = [0] * 12
                        for index, row in client_product_quantity_by_month.iterrows():
                            client_product_quantity_by_month_list[(index - 1)] = int(row.values[0])
                        client_payment = round(float(df.loc[(df['year'] == year) & (df['barcode'] == product)][df.loc[(df['year'] == year) & (df['barcode'] == product)]['channel'].isin([client])].agg({'payment':['sum']}).values[0]),2)

                        client_list_q.append([product] + [name_en] + [name_cn] + client_product_quantity_by_month_list + [sum(client_product_quantity_by_month_list)] + [client_payment])
                    this_client[client] = client_list_q
                this_year['pptx'] = this_client
                this_year['pptx_list'] = sale_client_list_order_p.index.tolist()

            
     




                response[year] = this_year
            
            
            return JsonResponse(response)
        except Exception as e:
            return HttpResponse(e)

    def get(self, request):
        return render(request, 'converter-tool/home.html')
 
