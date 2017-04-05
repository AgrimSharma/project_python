
import datetime
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from django.db.models import Sum, Count
from reports.report_api import ReportGenerator

from pdsr import calculate_charges
from service_centre.models import Shipment

today = datetime.datetime.today()


def pwp(end_date, end_month, end_year):
    report = ReportGenerator('weekly_performance_monitorr_MTD'+str(end_date)+'.xlsx')
    
    #today = str(end_year)+"-"+str(end_month)+"-"+str(end_day)
    enddate = datetime.date(end_year, end_month, end_date)
    # print enddate
    startdate = enddate - datetime.timedelta(days=7)
    #print type(start_date)
    MTD_start_date = datetime.date(end_year, end_month, 1)

    # 09/02-15/02 "2015-02-09"

    start_date = startdate.strftime("%Y-%m-%d")
    # print start_date
    end_date = enddate.strftime("%Y-%m-%d")
    MTD_start_date = MTD_start_date.strftime("%Y-%m-%d")
    # print MTD_start_date
    week = 'Week : '+startdate.strftime("%d-%m")+"-"+enddate.strftime("%d-%m")
    #awbs = sh.col_values(0)[1:]"
    col_heads = ('Particulars', week, 'MTD-Gross', 'Proj-Gross Mth' )
    report.write_header(col_heads)
    
    print 'weekly shipments ', start_date, end_date
    weekly_shipments = Shipment.objects.using('local_ecomm').filter(shipment_date__range=(start_date, end_date)).exclude(shipper_id=12)
    print weekly_shipments.count()
    MTD_gross_shipments = Shipment.objects.using('local_ecomm').filter(shipment_date__range=(MTD_start_date, end_date)).exclude(shipper_id=12)
    print 'monthly count ', MTD_start_date, end_date
    print MTD_gross_shipments.count()
    #Proj-Gross_Mth = 
    
    # Table rows start from here
    # Calculate sales using collectable_value
    # Populate Row 1
    Sales_PPD_INR_Mn =  weekly_shipments.filter(shipext__product__product_name='ppd').aggregate(cv=Sum("collectable_value")).get('cv')
    Sales_PPD_INR_Mn_MTD =  MTD_gross_shipments.filter(shipext__product__product_name='ppd').aggregate(cvm=Sum("collectable_value")).get('cvm')
    ROW1 = [ 'Sales-PPD (INR-Mn)', Sales_PPD_INR_Mn/1000000, Sales_PPD_INR_Mn_MTD/1000000]

    # Populate Row 2
    Sales_COD_INR_Mn = weekly_shipments.filter(shipext__product__product_name='cod').aggregate(cvc=Sum("collectable_value")).get('cvc')
    Sales_COD_INR_Mn_MTD = MTD_gross_shipments.filter(shipext__product__product_name='cod').aggregate(cvcm=Sum("collectable_value")).get('cvcm')
    ROW2 = [ 'Sales-COD (INR-Mn)', Sales_COD_INR_Mn/1000000, Sales_COD_INR_Mn_MTD/1000000]

    # Populate Row 3
    Total_INR_Mn = calculate_charges(date_range=start_date) 
    Total_INR_Mn_MTD = calculate_charges(date_range=MTD_start_date) 
    ROW3 = [ 'Total', Total_INR_Mn/1000000, Total_INR_Mn_MTD/1000000]

    # Calculate PPD, COD volumes
    # Populate Row 4
    Volumes_PPD = weekly_shipments.filter(product_type='ppd').count()
    Volumes_PPD_MTD = MTD_gross_shipments.filter(product_type='ppd').count()
    ROW4 = [ 'Volumes-PPD', Volumes_PPD, Volumes_PPD_MTD]
    
    # Populate Row 5
    Volumes_COD = weekly_shipments.filter(product_type='cod').count()
    Volumes_COD_MTD = MTD_gross_shipments.filter(product_type='cod').count()
    ROW5 = [ 'Volumes-COD', Volumes_COD, Volumes_COD_MTD]

    # Populate Row 6
    Volumes_Total = Volumes_PPD + Volumes_COD
    Volumes_Total_MTD = Volumes_PPD_MTD + Volumes_COD_MTD
    ROW6 = [ 'Total', Volumes_Total, Volumes_Total_MTD ]
    
    # Populate Row 7
    Yield_per_Shipt_PPD_INR = Sales_PPD_INR_Mn/Volumes_PPD
    Yield_per_Shipt_PPD_INR_MTD = Sales_PPD_INR_Mn_MTD/Volumes_PPD_MTD
    ROW7 = [ 'Yield/Shipt-PPD-INR', Yield_per_Shipt_PPD_INR,  Yield_per_Shipt_PPD_INR_MTD] 

    # Populate Row 8 
    Yield_per_Shipt_COD_INR = Sales_COD_INR_Mn/Volumes_COD
    Yield_per_Shipt_COD_INR_MTD = Sales_COD_INR_Mn_MTD/Volumes_COD_MTD
    ROW8 = [ 'Yield/Shipt-COD-INR', Yield_per_Shipt_COD_INR, Yield_per_Shipt_COD_INR_MTD]
    
    # Populate Row 9
    Total_Yield_per_Shipt_INR = Total_INR_Mn/Volumes_Total
    Total_Yield_per_Shipt_INR_MTD = Total_INR_Mn_MTD/Volumes_Total_MTD
    ROW9 = ['Yield/Shipt-Total', Total_Yield_per_Shipt_INR, Total_Yield_per_Shipt_INR_MTD ]

    # Populate Row 10
    Sales_Ratio_PPD = Sales_PPD_INR_Mn/Volumes_PPD
    Sales_Ratio_PPD_MTD = Sales_PPD_INR_Mn_MTD/Volumes_PPD_MTD

    ROW10= [ 'Sales Ratio_PPD', Sales_Ratio_PPD, Sales_Ratio_PPD_MTD]
    
    # Populate Row 11
    Sales_Ratio_COD = Sales_COD_INR_Mn/Volumes_COD
    Sales_Ratio_COD_MTD = Sales_COD_INR_Mn_MTD/Volumes_COD_MTD

    ROW11= [ 'Sales Ratio-COD', Sales_Ratio_COD_MTD, Sales_Ratio_COD_MTD]

    # Populate Row 12
    Volumes_Ratio_PPD =  Volumes_PPD/weekly_shipments.count()
    Volumes_Ratio_PPD_MTD =  Volumes_PPD_MTD/MTD_gross_shipments.count()
    ROW12 = [ 'Volumes Ratio-PPD', Volumes_Ratio_PPD, Volumes_Ratio_PPD ]
    
    # Populate Row 13
    Volumes_Ratio_COD =  Volumes_COD/weekly_shipments.count()
    Volumes_Ratio_COD_MTD =  Volumes_COD_MTD/MTD_gross_shipments.count()
    ROW13 = [ 'Volumes Ratio-COD', Volumes_Ratio_PPD, Volumes_Ratio_PPD  ]

    # Populate Row 14
    No_of_Towns = weekly_shipments.values('original_dest__city').distinct().count()
    ROW14 = [ 'No of Towns', 0, No_of_Towns ]

    # Populate Row 15
    No_of_DCs =  weekly_shipments.values('original_dest').distinct().count()
    ROW15 = [ 'No of DCs', 0, No_of_DCs ]

    # Populate Row 16
    No_of_Pincodes =  weekly_shipments.values('pincode').distinct().count()
    ROW16 = [ 'No of Towns', 0, No_of_Pincodes]

    report_body = [ROW1, ROW2, ROW3, ROW4, ROW5, ROW6, ROW7, ROW8, ROW9, ROW10, ROW11, ROW12, ROW13, ROW14, ROW15, ROW16]
    
    '''
    for i in xrange(1, 17):
        j = "ROW"+str(i)
        report_body.append(j)
    
    for awb in awbs:
        print awb
        data = Shipment.objects.get(airwaybill_number=awb)
        row_data = (data.airwaybill_number, data.deliveryoutscan_set.filter().count())
        report.write_row(row_data)
    '''

    report.write_body(report_body)
    report.manual_sheet_close()

if __name__=="__main__":
	pwp(end_date=25, end_month=02, end_year=2015)

