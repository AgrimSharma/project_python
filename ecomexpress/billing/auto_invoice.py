from reportlab.lib import colors, utils
from reportlab.lib.units import mm, inch, cm
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib import styles
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Image
from reportlab.rl_config import defaultPageSize
from django.conf import settings
from billing.number_to_words import Number2Words

from datetime import date, timedelta
#from converter import mainfunction
import xlrd

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
 
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CenterHeading', alignment=TA_CENTER, fontSize=10))
styles.add(ParagraphStyle(name='LeftHeading', alignment=TA_LEFT, fontSize=10))
styles.add(ParagraphStyle(name='RightHeading', alignment=TA_RIGHT, fontSize=10))
styles.add(ParagraphStyle(name='bold_right', alignment=TA_RIGHT, fontSize=10))
styles.add(ParagraphStyle(name='bold_left', alignment=TA_LEFT, fontSize=10))
styles.add(ParagraphStyle(name='bold_last', alignment=TA_CENTER, fontSize=8))
styles.add(ParagraphStyle(name='invoice', alignment=TA_CENTER, fontSize=12))
styles.add(ParagraphStyle(name='footer', fontSize=6))
styles.add(ParagraphStyle(name='image', alignment=TA_RIGHT, fontSize=8))

PROJECT_ROOT = '/home/web/ecomm.prtouch.com/ecomexpress/'
img_location = PROJECT_ROOT + '/static/assets/img/EcomlogoPdf.png'

def summary_reader(filename):
    workbook = xlrd.open_workbook(filename)
    worksheet = workbook.sheet_by_name('Summary')
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = -1
    sdata = []
    manpower_total = 0
    line_haul = 0
    while curr_row < num_rows:
        curr_row += 1
        row = worksheet.row(curr_row)
        curr_cell = -1
        data = []
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text,
            # 2=Number, 3=Date, 4=Boolean,
            # 5=Error, 6=Blank
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            if curr_row == 1 and curr_cell == 1:
                manpower_total = cell_value
            if curr_row == 2 and curr_cell == 1:
                line_haul = cell_value
            if cell_type == 1:
                data.append(cell_value)
            else:
                rounded_data = "{0:.2f}".format(round(cell_value, 2))
                data.append(rounded_data)
        sdata.append(data)
    return sdata, manpower_total, line_haul

def manpower_reader(filename):
    workbook = xlrd.open_workbook(filename)
    #worksheet = workbook.sheet_by_name("Manpower_Dec'14")
    worksheet = workbook.sheet_by_index(1)
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = -1
    sdata = []
    while curr_row < num_rows:
        curr_row += 1
        row = worksheet.row(curr_row)
        curr_cell = -1
        data = []
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text,
            # 2=Number, 3=Date, 4=Boolean,
            # 5=Error, 6=Blank
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            if cell_type == 3:
                date_tuple = xlrd.xldate_as_tuple(cell_value, workbook.datemode)
                date = str(date_tuple[2])+ '-' + str(date_tuple[1])+ '-' + str(date_tuple[0])
                data.append(date)
            elif cell_type == 1 or cell_type == 0:
                data.append(cell_value)
            else:
                data.append(int(round(cell_value)))
        sdata.append(data)
    return sdata, worksheet.ncols

def tax_calculation(gross_total):
    service_tax = 0.12 * gross_total
    education_cess = 0.02 * service_tax
    hse_cess = 0.01 * service_tax
    return service_tax, education_cess, hse_cess

def generate_invoice_pdf(invoice_no, customer, filename, with_header):
    print 'start generating pdfs for bill ...'
    if with_header:
        tail_string = customer + 'with_header'
    else:
        tail_string = customer + 'without_header'
    output_file_name = PROJECT_ROOT + 'static/uploads/billing/auto_invoice_{0}_{1}.pdf'.format(invoice_no, tail_string)
    doc = SimpleDocTemplate(output_file_name, pagesize=A4, topMargin=50,
              bottomMargin=30, leftMargin=60, rightMargin=60)
    elements = []
    img_data = '''
        <para><img src="%s" width="84" height="35" valign="0"/><br/>
        </para>''' % img_location
    img = Paragraph(img_data, styles['Normal'])

    account_data, manpower_total, line_haul = summary_reader(filename)
    manpower_total = int(round(manpower_total))
    line_haul = int(round(line_haul))
    g_total = manpower_total + line_haul

    # adding logo
    def adding_logo(with_header):
        if with_header:
            img_table = Table([['', '', img]], colWidths=(125, 350, 100))
        else:
            img_table = Table([['', '', '']], colWidths=(125, 350, 100))
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(img_table)

    # invoice para
    def invoice_para(with_header):
        invoice_para ='''
            <para><b>INVOICE</b></para>'''
        ip = Paragraph(invoice_para, styles['invoice'])
        if with_header:
            invoice_table = Table([[img, ip, '']], colWidths=(250, 100, 250))
        else:
            invoice_table = Table([['', ip, '']], colWidths=(250, 100, 250))
        invoice_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 10))


    def myFirstPage(canvas, doc):
        Title = "Hello world"
        canvas.saveState()
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "")
        canvas.restoreState()
        
    # later page footer
    def myLaterPages(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        footer_para = '''
            <para>
            <b>ECOM EXPRESS PRIVATE LIMITED</b>
            Corporate Office:14/12/2,Samalka,Old Delhi-Gurgaon
            Road,New Delhi-110037(INDIA) Registered Office:C-509,Vardhaman<br/> 
            Apartments,Plot No.3,Mayur Vihar Phase-I Extension,Delhi-110091(INDIA)
            CIN:U63000DL2012PTC241107|Tel.:+911130212000|www.ecomexpress.in</para>'''
        P = Paragraph(footer_para, styles['footer'])
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

    # Ecom address
    def address():
        data = [[
            Paragraph('''<para><b>Ecom Express PrivateLimited</b></para>''', 
            styles['CenterHeading'])],
            ['No. 14/12/2, Samalkha, Old Delhi Gurgaon Road, New Delhi-110 037 (India)'],
            ['Tel. No: 001-30212000, Website: www.ecomexpress.in']]
        ecom_table = Table(data, colWidths=(575))
        ecom_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25,colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        elements.append(ecom_table)

    # Billed to
    def billed_to():
        billed_data = [[
            Paragraph('''<para><b>BILLED TO:</b></para>''',
            styles['CenterHeading']), '']]
        billed_table = Table(billed_data, colWidths=(300, 275))
        billed_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25,colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        elements.append(billed_table)

    # Billing address
    def billing_address(invoice_no, customer):
        if customer == "tv18":
            para = '''
                <para>11007<br/>TV18 HOME SHOPPING NETWORK<br/>FC-24<br/>
                7th Floor<br/>Sector 16A<br/>Film City<br/>NOIDA UTTERPRADESH<br/>
                201301<br/>Phone No: 123</para>'''
        else:
            para = '''
                <para>71237<br/>DENTSPLY INDIA PRIVATE LIMITED<br/>
                PLOT NO.358<br/>FIES PATPARGANJ<br/>INDUSTRIAL AREA<br/>
                DELHI-110092<br/>Phone No: 011-47529683</para>'''
        address_para = Paragraph(para, styles['Normal'])
        today = date.today()
        first_day = '1-%s-%s' % (today.month, today.year)
        table_data = [[
            'Invoice number', str(invoice_no)], ['Date', first_day]]
        t = Table(table_data, colWidths=(175, 100), rowHeights=(20,20))
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'), 
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        some_data = [(address_para, t)]
        main_table = Table(some_data, colWidths=(300, 275),rowHeights=(120,))
        main_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 2),
            ('LEFTPADDING', (1, 0), (1, 0), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        elements.append(main_table)

    # Remark section
    def remark():
        today = date.today()
        rday = today - timedelta(days=30)
        remark_para = '''
            <para>Being the amount debited to your account towards ECOM Branded
            Services(EBS)services provided in the <br/>month of %s at various 
            cities as per list enclosed</para>''' % rday.strftime("%B-%Y").upper() 
        remark = Paragraph(remark_para, styles['Normal'])
        remark_data = [[
            Paragraph('''<para><b>Remarks:</b></para>''',styles['Normal'])], 
            [remark]]
        remark_table = Table(remark_data, colWidths=(575))
        remark_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        elements.append(remark_table)

    # Particular
    def particular(amount, linehaul):
        manpower_para = '''
            <para>Manpower(277 emp.) @Rs.25,000 (Location wise detail<br/>attached in 
            annexure)</para>'''
        manpower = Paragraph(manpower_para, styles['Normal'])
        particular_data = [[
            Paragraph('''<para><b>Sl. No.</b></para>''', styles['CenterHeading']), 
            Paragraph('''<para><b>Particulars</b></para>''', styles['CenterHeading']),
            Paragraph('''<para><b>Amount</b></para>''', styles['CenterHeading'])],
            ['1', manpower, str(amount)],
            ['2', 'Line Haul charges as per detail attached in annexure', str(linehaul)],
            ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''], ['', '', ''],
            ['', '', '']]
        particular_table = Table(particular_data, colWidths=(50, 400, 125))
        particular_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (2, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, 1), 'CENTER'),
            ('ALIGN', (1, 1), (1, 1), 'LEFT'),
            ('ALIGN', (2, 1), (2, 1), 'RIGHT'),
            ('ALIGN', (0, 2), (0, 2), 'CENTER'),
            ('ALIGN', (1, 2), (1, 2), 'LEFT'),
            ('ALIGN', (2, 2), (2, 2), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        elements.append(particular_table)

    # summary
    def summary():
        summary_table = Table([[
            Paragraph('''<para><b>Summary</b></para>''',
            styles['CenterHeading'])]], colWidths=(575))
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        elements.append(summary_table)

    # Gross total
    def gross_total(g_total):
        gross_table = Table([[
            '',Paragraph('''<para><b>GROSS TOTAL</b></para>''',
            styles['bold_right']), 
            Paragraph('''<para><b>%s</b></para>''' % str(g_total),
            styles['bold_right'])]], colWidths=(50, 400, 125))
        gross_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        elements.append(gross_table)

    # Cess and Tax
    def cess_tax(g_total):
        servicetax, educess, hsecess = tax_calculation(g_total)
        cess_data = [
            ['', 'Service Tax', '12.00%', "{0:.2f}".format(round(servicetax, 2))],
            ['', 'Education Cess', '2.00%', "{0:.2f}".format(round(educess,2))],
            ['', 'HSE Cess', '1.00%', "{0:.2f}".format(round(hsecess,2))]]
        cess_table = Table(cess_data, colWidths=(50, 400, 65, 60))
        cess_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        elements.append(cess_table)
    
    #total
    def total(g_total):
        servicetax, educess, hsecess = tax_calculation(g_total)
        total = servicetax + educess + hsecess + g_total
        total_string = "{0:.2f}".format(round(total,2))
        total_table = Table([[
            Paragraph('''<para><b>TOTAL</b></para>''', styles['bold_right']),
            Paragraph('''<para><b>%s</b></para>''' % total_string,
            styles['bold_right'])]], 
            colWidths=(450, 125))
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
        elements.append(total_table)
    
    # inwords
    def inwords(gross_total):
        servicetax, educess, hsecess = tax_calculation(gross_total)
        grand_total = servicetax + educess + hsecess + gross_total
        wGenerator = Number2Words()
        total_in_words = wGenerator.convertNumberToWords(int(grand_total))

        inword_para = '''<para><b>In</b><br/><b>Words:</b></para>'''
        inword = Paragraph(inword_para, styles['Normal'])
        rsword_para = '''<para>%s only</para>''' % total_in_words
        rsword = Paragraph(rsword_para, styles['Normal'])
        inwords_table = Table([[inword, rsword]], colWidths=(50, 525))
        inwords_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(inwords_table)

    # Company Details
    def company_details():
        companydetails_table = Table([[
            Paragraph('''<para><b>Company Details:</b></para>''', styles['bold_left']),
            Paragraph('''<para><b>For Ecom Express Private Limited</b></para>''', 
            styles['bold_left'])]], colWidths=(350, 225))
        companydetails_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(companydetails_table)

    # pan details
    def pan_details(customer):
        if customer == "tv18":
            pan_data = [['PAN No.', Paragraph('''<para><b>AADCE1344F</b></para>''', styles['CenterHeading'])],
	            ['Service Tax Regist', Paragraph('''<para><b>AADCE1344FSD001</b></para>''', styles['CenterHeading'])],
	            ['VAT/TIN', Paragraph('''<para>NA</para>''', styles['CenterHeading'])],
	            ['CST', Paragraph('''<para>NA</para>''', styles['CenterHeading'])]]
        pan_table = Table(pan_data, colWidths=(175, 175))
        pan_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        para_data = '''
            <para><br/><br/><b>Signed</b><br/></para>'''
        empty_para = Paragraph(para_data, styles['CenterHeading'])
        some_data = [(pan_table, empty_para)]
        merge_table = Table(some_data, colWidths=(350, 225))
        merge_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(merge_table)

    # Authorized signatory
    def authorized_signatory():
        auth_table = Table([[
            Paragraph('''<para><b>CIN</b></para>''', styles['bold_left']), 
            Paragraph('''<para><b>U63000DL2012PTC241107</b></para>''', styles['bold_left']), 
            Paragraph('''<para><b>Authorized Signatory</b></para>''', styles['bold_left'])]], 
            colWidths=(175, 175, 225))
        auth_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(auth_table)
    
    # Debit/Credit
    def debit_credit():
        debit_table = Table([['This is a computerised generated Debit/Credit Note']], 
            colWidths=(575))
        debit_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(debit_table)
        elements.append(Spacer(1, 36))

    # Account Head
    def account_head():
        account_table = Table(account_data, colWidths=(125, 200, 125, 125))
        account_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(account_table)
        elements.append(Spacer(1, 590))

    # Annexure of Manpower
    def annexure_of_manpower(filename):
        if not with_header:
            elements.append(Spacer(1, 20))

        elements.append(Spacer(1, 24))
        manpower_data, ncols = manpower_reader(filename)
        # col_width_list = (115, 75, 75, 75, 75, 75) # [575/ncols for x in range(1, 7)]
        col_width_list = [105] + [470/(ncols-1) for x in range(ncols-1)]
        manpower_table = Table(manpower_data, colWidths=col_width_list)
        manpower_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(manpower_table)

    
    # building the document
    invoice_para(with_header)
    address()
    billed_to()
    billing_address(invoice_no, customer)
    remark()
    particular(manpower_total, line_haul)
    summary()
    gross_total(g_total)
    cess_tax(g_total)
    total(g_total)
    inwords(g_total)
    company_details()
    pan_details(customer)
    authorized_signatory()
    debit_credit()
    adding_logo(with_header)
    account_head()
    adding_logo(with_header)
    annexure_of_manpower(filename)
    doc.build(elements, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    print 'pdf document %s generated ' % output_file_name
    return output_file_name

#generate_invoice_pdf(1688, "dentsply", '/tmp/ebs_tv18.xls', True)
