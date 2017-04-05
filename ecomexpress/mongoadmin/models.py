import datetime as dt
import pymongo as pm

from django.db import models

connection = pm.MongoClient('172.31.4.7', 27017)

db = connection['ecomm']


def write_shipment_correction(awb, emp, correction_type):
    """
    Correction:
        awb: airwaybill_number
        date: correction_date
        remark: "collectable value updated / pod correction"
        emp: employee_code
        sc: service_center at which correction happened /
            employee service center.
        correction_type = 0 - collectable value
                          1 - pod correction
    """
    correction = db['correction']

    remark_dict = {
        0:'collectable value',
        1:'POD correction'
    }
    remark = remark_dict.get(int(correction_type), correction_type)
    data = {
        'awb': awb, 'date': dt.datetime.today(), 'remark': remark,
        'sc': emp.service_centre.center_name, 'emp': emp.employee_code}
    correction_obj = correction.insert_one(data)
    return correction_obj

def view_shipment_correction(date_from, date_to):
    # get the correction collection (table)
    correction = db['correction']
    # get the date range
    start_time = dt.datetime.strptime(date_from, '%Y-%m-%d')
    end_time = dt.datetime.strptime(date_to, '%Y-%m-%d')
    end_time = end_time.replace(hour=23, minute=59, second=59)

    return correction.find({'date': {"$gte":start_time, "$lt":end_time}}).sort([('date', -1)])

def add_ledger_name(code, ledger_name):
    """ customer:
        code: airwaybill_number
        ledger_name: correction_date """

    customer = db['customer']
    customer = customer.update(
        {'code': int(code)}, 
        {"$set": {"ledger_name": ledger_name, 'updated_on': dt.datetime.now()}}, True)
    return customer 

def get_ledger_name(code):
    customer = db['customer']
    data = customer.find_one({'code': int(code)})
    return data.get('ledger_name') if data else ''

def get_ledger_name_list():
    customer = db['customer']
    data = customer.find({}).sort('code')
    return [(customer.get('code'), customer.get('ledger_name')) 
            for customer in data]
