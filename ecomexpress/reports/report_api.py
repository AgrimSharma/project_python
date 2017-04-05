import datetime
import calendar
import os
import zipfile
import csv
from xlsxwriter.workbook import Workbook

from django.conf import settings


def generate_zip(file_name, args):
    base_path = settings.PROJECT_ROOT + '/static/uploads/reports/'
    base_url = settings.ROOT_URL + '/static/uploads/reports/'
    zip_file = zipfile.ZipFile(base_path + file_name, 'w', compression=zipfile.ZIP_DEFLATED)
    for arg in args:
        zip_file.write(base_path + arg, os.path.basename(arg), zipfile.ZIP_DEFLATED)
    zip_file.close()
    return base_url + file_name

def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

class ReportGenerator(object):

    def __init__(self, file_name, border=False):
        self.file_name = file_name
        self.path_to_save = settings.FILE_UPLOAD_TEMP_DIR + '/reports/' + file_name
        self.workbook = Workbook(self.path_to_save, {'constant_memory': True})
        self.row_num = 0

        # define style formats for header and data
        self.header_format = self.workbook.add_format()
        self.header_format.set_bg_color('yellow')
        self.header_format.set_bold()

        self.plain_format = self.workbook.add_format()
        if border:
            self.header_format.set_border()
            self.plain_format.set_border()

        # add a worksheet and set excel sheet column headers
        self.sheet = self.workbook.add_worksheet()

    def write_details(self, *args):
        """ used to write report details like report name, date of report"""
        for arg in args:
            self.sheet.write(self.row_num, 5, arg, self.header_format)
            self.row_num += 1
        self.row_num += 1

    def write_header(self, col_heads):
        """ write report headers """
        col_count = len(col_heads)
        self.sheet.set_column(self.row_num, col_count, 12) # set column width
        # add filename and set save file path
        for col, name in enumerate(col_heads):
            self.sheet.write(self.row_num, col, name, self.header_format)
        self.row_num += 1

    def removeNonAscii(self, str):
        return "".join(i for i in str if ord(i)<128)

    def manual_sheet_close(self):
        self.workbook.close()
        return self.file_name

    def write_body(self, body):
        """ used to write the body of the report"""
        for row in body:
            for col, val in enumerate(row):
                value = val.encode('ascii', 'ignore') if isinstance(val, unicode) else str(val)
                self.sheet.write_string(self.row_num, col, value) #, self.plain_format)
                #self.sheet.write(self.row_num, col, value, self.plain_format)
            self.row_num += 1

        self.workbook.close()
        return self.file_name

    def write_matrix(self, body):
        """ used to write the body of the report"""
        for row in body:
            for col, val in enumerate(row):
                value = val.encode('ascii', 'ignore') if isinstance(val, unicode) else str(val)
                self.sheet.write_string(self.row_num, col, value) #, self.plain_format)
                #self.sheet.write(self.row_num, col, value, self.plain_format)
            self.row_num += 1

    def write_row(self, row):
        for col, val in enumerate(row):
            value = val.encode('ascii', 'ignore') if isinstance(val, unicode) else str(val)
            #self.sheet.write(self.row_num, col, val, self.plain_format)
            self.sheet.write_string(self.row_num, col, value)
        self.row_num += 1

    def current_month_range(self):
        month = datetime.date.today().month
        year = datetime.date.today().year
        day = datetime.date.today().day

        month_range = calendar.monthrange(year, month)

        start_date = datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
        end_date = datetime.datetime(year, month, day).strftime('%Y-%m-%d')
        return (start_date, end_date)

    def last_month_range(self):
        month = datetime.date.today().month - 1
        month = 12 if month == 0 else month

        year = datetime.date.today().year
        year = year - 1 if month == 12 else year

        month_range = calendar.monthrange(year, month)
        start_date = datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
        end_date = datetime.datetime(year, month, month_range[1]).strftime('%Y-%m-%d')
        return (start_date, end_date)


class CSVReportGenerator(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.base_path = settings.FILE_UPLOAD_TEMP_DIR + '/reports/'
        self.full_path = self.base_path + self.file_name
        file_path, extension = os.path.splitext(self.full_path)
        self.compressed_file_path = file_path + '.zip'
        self.open_file = open(self.full_path, "wb")
        self.mywriter = csv.writer(self.open_file)

    def write_row(self, row):
        data = [val.encode('ascii', 'ignore') if isinstance(val, unicode) else str(val) for val in row]
        self.mywriter.writerow(data)

    def get_file_path(self):
        return self.full_path

    def compress_file(self):
        os.system('cd {0} && zip -j {1} {2}'.format(self.base_path, self.compressed_file_path, self.full_path))
        return self.compressed_file_path
