'''
Created on Dec 29, 2012

@author: Sirius
'''
import xlrd
from ecomm_admin.models import *

wb=xlrd.open_workbook('status.xls')
sh = wb.sheet_by_index(0)
for rownum in range(1,sh.nrows):
    if rownum <> 2 and rownum <> 46:
        val = sh.row_values(rownum) 
        ShipmentStatusMaster.objects.create(code=int(val[0]), code_description=val[1])
        print rownum, val[0], val[1]