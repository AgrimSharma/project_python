from reportlab.lib import colors, utils
from reportlab.lib.units import mm, inch, cm
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import Paragraph, SimpleDocTemplate,\
    Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib import styles
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Image
from reportlab.rl_config import defaultPageSize
from django.conf import settings
from billing.models import Billing
from customer.models import Product
from service_centre.models import Shipment


PROJECT_ROOT = settings.PROJECT_ROOT
img_location = PROJECT_ROOT + '/static/assets/img/EcomlogoPdf.png'
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

def tax_calculation(gross_total):
    service_tax = 0.12 * gross_total
    education_cess = 0.02 * service_tax
    hse_cess = 0.01 * service_tax
    return service_tax

def generate_invoice_pdf(bill_id, with_header=True):
    print '5.1.1 start generating pdfs for bill ...',bill_id
    #billing = Billing.objects.get(id=bill_id)
    if with_header:
        full_file_name = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/reports/tv18_ebs_invoice_report_{0}.pdf'.format(bill_id)
    else:
        full_file_name = '/home/web/ecomm.prtouch.com/ecomexpress/static/uploads/reports/tv18_ebs_invoice_report_without_head_{0}.pdf'.format(bill_id)
    doc = SimpleDocTemplate(full_file_name, pagesize=A4, topMargin=50,
              bottomMargin=30, leftMargin=60, rightMargin=60)
    print '5.1.2 pdf doc generated '
    elements = []
    
    # adding logo
    if with_header:
        img_data = '''
               <para>
               <img src="%s" width="84" height="35" valign="0"/><br/>
               </para>''' % img_location
        img = Paragraph(img_data, styles['Normal'])
        # Invoice header
        invoice_para = '''
		    <para>
		    <b>INVOICE</b>
		    </para>
		    '''
        ip = Paragraph(invoice_para, styles['invoice'])
        invoice_table = Table([[img, ip, '']], colWidths=(250, 50, 280))
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 10))
    else:
        elements.append(Spacer(1, 30))
    
    # Ecom address
    data = [[Paragraph('''<para><b>Ecom Express Private Limited</b></para>''', styles['CenterHeading'])],
	    ['No. 14/12/2, Samalkha, Old Delhi Gurgaon Road, New Delhi-110 037 (India)'],
	    ['Tel. No: 001-30212000, Website: www.ecomexpress.in']]
    ecom_table = Table(data, colWidths=(450))
    ecom_table.setStyle(TableStyle([
	    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
	    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
	    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
	    ('FONTSIZE', (0, 0), (-1, -1), 8),
	    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
	    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(ecom_table)
    
    # Billed to
    billed_data = [[Paragraph('''<para><b>BILLED TO:</b></para>''', styles['CenterHeading']), '']]
    billed_table = Table(billed_data, colWidths=(250, 200))
    billed_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(billed_table)
    
    # Billing address
    para = '''
	    <para>
	    11007<br/>
	    TV18 HOME SHOPPING NETWORK<br/>
	    FC-24<br/>
	    7th Floor<br/>
	    Sector 16A<br/>
	    Film City<br/>
	    NOIDA UTTERPRADESH<br/>
	    201301<br/>
	    Phone No: 123
	    </para>
	    '''
    address_para = Paragraph(para, styles['Normal'])
    table_data = [['Invoice number', '1685'],
	          ['Date', '1-Oct-2014']]
    t = Table(table_data, colWidths=(100, 100), rowHeights=(20, 20))
    t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    some_data = [(address_para, t)]
    main_table = Table(some_data, colWidths=(250, 200), rowHeights=(120,))
    main_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 2),
            ('LEFTPADDING', (1, 0), (1, 0), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(main_table)
    
    # Remark section
    remark_para = '''
	    <para>
	    Being the amount debited to your account towards ECOM Branded Services(EBS)<br/>
	    services provided in the month of SEPTEMBER 2014 at various cities as per list enclosed
	    </para>
	    '''
    remark = Paragraph(remark_para, styles['Normal'])
    remark_data = [[Paragraph('''<para><b>Remarks:</b></para>''', styles['Normal'])], [remark]]
    remark_table = Table(remark_data, colWidths=(450))
    remark_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(remark_table)
    
    # Partcular
    manpower_para = '''
	    <para>
	    Manpower@Rs.25,000 (Location wise detail<br/>
	    attached in annexure)
	    </para>
	    '''
    manpower = Paragraph(manpower_para, styles['Normal'])
    particular_data = [[Paragraph('''<para><b>Sl. No.</b></para>''', styles['CenterHeading']), Paragraph('''<para><b>Particulars</b></para>''', styles['CenterHeading']), Paragraph('''<para><b>Amount</b></para>''', styles['CenterHeading'])],
		       ['1', manpower, '33,05,833.00'],
		       ['2', 'Line Haul charges as per detail attached in annexure', '12,84,314'],
		       ['', '', ''],
                       ['', '', ''],
                       ['', '', ''],
                       ['', '', ''],
                       ['', '', ''],
                       ['', '', '']]
    particular_table = Table(particular_data, colWidths=(50, 300, 100))
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
			    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
 			    ]))
    elements.append(particular_table)
    
    # summary
    summary_table = Table([[Paragraph('''<para><b>Summary</b></para>''', styles['CenterHeading'])]], colWidths=(450))
    summary_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(summary_table)
    
    # Gross total
    gross_table = Table([['', 
        Paragraph('''<para><b>GROSS TOTAL</b></para>''', styles['bold_right']), 
        Paragraph('''<para><b>45,90,147.00</b></para>''', styles['bold_right'])]], 
        colWidths=(50, 300, 100))
    gross_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(gross_table)
    
    # Cess and Tax
    cess_data = [['', 'Service Tax', '12.00%', '5,50,817.64'],
	         ['', 'Education Cess', '2.00%', '11,016.35'],
	         ['', 'HSE Cess', '1.00%', '5,508.17']]
    cess_table = Table(cess_data, colWidths=(50, 300, 50, 50))
    cess_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(cess_table)
    
    # total
    total_table = Table([[
        Paragraph('''<para><b>TOTAL</b></para>''', styles['bold_right']), 
        Paragraph('''<para><b>51,57,489</b></para>''', styles['bold_right'])]], colWidths=(350, 100))
    total_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(total_table)
    
    # total
    inword_para = '''
	    <para>
	    <b>In</b><br/>
	    <b>Words:</b>
	    </para>
	    '''
    inword = Paragraph(inword_para, styles['Normal'])
    rsword_para = '''
	    <para>
	    Rs. Fifty One Lakh Fifty Seven Thousand Four Hundred and Eighty Nine<br/>
	    only
	    </para>
	    '''
    rsword = Paragraph(rsword_para, styles['Normal'])
    inwords_table = Table([[inword, rsword]], colWidths=(50, 400))
    inwords_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(inwords_table)
    
    # Company Details
    companydetails_table = Table(
        [
            [
                Paragraph(
                    '''<para><b>Company Details:</b></para>''', styles['bold_left']
                ),
                Paragraph(
                    '''<para><b>For Ecom Express Private Limited</b></para>''', styles['bold_left']
                )
            ]
        ],
        colWidths=(250, 200)
    )
    companydetails_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(companydetails_table)
    
    # pan details
    pan_data = [['PAN No.', Paragraph('''<para><b>AADCE1344F</b></para>''', styles['CenterHeading'])],
	        ['Service Tax Regist', Paragraph('''<para><b>AADCE1344FSD001</b></para>''', styles['CenterHeading'])],
	        ['VAT/TIN', Paragraph('''<para>NA</para>''', styles['CenterHeading'])],
	        ['CST', Paragraph('''<para>NA</para>''', styles['CenterHeading'])]]
    pan_table = Table(pan_data, colWidths=(100, 150))
    pan_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    para_data = '''
           <para>
           </br>
           </br>
           <b>Signed</b></br>
           </para>
           '''
    empty_para = Paragraph(para_data, styles['CenterHeading'])
    some_data = [(pan_table, empty_para)]
    merge_table = Table(some_data, colWidths=(250, 200))
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
    # Company Details
    auth_table = Table([[Paragraph('''<para><b>CIN</b></para>''', styles['bold_left']), Paragraph('''<para><b>U63000DL2012PTC241107</b></para>''', styles['bold_left']), Paragraph('''<para><b>Authorized Signatory</b></para>''', styles['bold_left'])]], colWidths=(100, 150, 200))
    auth_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(auth_table)
    
    # Debit/Credit
    debit_table = Table([['This is a computerised generated Debit/Credit Note']], colWidths=(450))
    debit_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(debit_table)
    elements.append(Spacer(1, 36))
    
    # adding logo
    img_data = '''
               <para>
               <img src="%s" width="84" height="35" valign="0"/><br/>
               </para>''' % img_location
    img = Paragraph(img_data, styles['image'])
    
    secondpage_table = Table([['', '', img]], colWidths=(100, 100, 400))
    secondpage_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        #('ALIGN', (0, -1), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(secondpage_table)
    
    # Account Head
    account_data = [[
        Paragraph('''<para><b>Account Head</b></para>''', styles['CenterHeading']),
        Paragraph('''<para><b>Billing amount excl ST</b></para>''', styles['CenterHeading']),
        Paragraph('''<para><b>Service Tax</b></para>''', styles['CenterHeading']),
        Paragraph('''<para><b>Total</b></para>''', styles['CenterHeading'])
        ],
        ['Employees', '33,05,833', '4,08,601', '37,14,434'],
        ['Line Haul', '12,84,314', '1,58,741', '14,43,055'],
        ['Total', '45,90,147', '5,67,342', '51,57,489']
    ]
    account_table = Table(account_data, colWidths=(100, 200, 100, 100))
    account_table.setStyle(TableStyle([
           ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('FONTSIZE', (0, 0), (-1, -1), 8),
           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(account_table)
    elements.append(Spacer(1, 590))
    
    # adding logo
    img_data = '''
               <para>
               <img src="%s" width="84" height="35" valign="0"/><br/>
               </para>''' % img_location
    img = Paragraph(img_data, styles['image'])
    
    # Invoice header
    thirdpage_table = Table([['', '', img]], colWidths=(100, 100, 400))
    thirdpage_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(thirdpage_table)
    
    elements.append(Spacer(1, 24))
    # Annexure of Manpower
    single_data = Paragraph('''<para><b>Annexure of Manpower</b></para>''', styles['Normal'])
    single_table = Table([[single_data, '', '']], colWidths=(250, 100, 100))
    single_table.setStyle(TableStyle([
	    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
	    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
	    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.append(single_table)

    manpower_data = [[Paragraph('''<para><b>Pick up-Origin</b></para>''', styles['LeftHeading']), Paragraph('''<para><b>1/Sept/2014</b></para>''', styles['RightHeading']), Paragraph('''<para><b>3/Sept/2014</b></para>''', styles['RightHeading']), Paragraph('''<para><b>24/Sept/2014</b></para>''', styles['RightHeading']), Paragraph('''<para><b>26/Sept/2014</b></para>''', styles['RightHeading']), Paragraph('''<para><b>TOTAL</b></para>''', styles['RightHeading'])],
		     ['AGRA-AGR', '15', '-', '-', '-', '15'],
		     ['BIKANER-BIK', '9', '-', '-', '-', '9'],
		     ['DEHRADUN-DRB', '-', '4', '-', '-', '4'],
		     ['DELHI-DLD', '8', '-', '-', '-', '8'],
		     ['DELHI-DLO', '8', '-', '-', '-', '8'],
		     ['DELHI-DLW', '7', '-', '-', '-', '7'],
		     ['DELHI-DSW', '5', '-', '-', '-', '5'],
		     ['FARIDABAD-FAR', '4', '-', '-', '-', '4'],
		     ['GWALIOR-GWL', '6', '-', '-', '-', '6'],
		     ['JODHPUR-JOD', '9', '-', '-', '-', '9'],
		     ['LUCKNOW-LKB', '4', '-', '-', '-', '4'],
		     ['LUCKNOW-LKC', '5', '-', '-', '-', '5'],
		     ['LUCKNOW-LKA', '4', '-', '-', '-', '4'],
		     ['MEERUT-MEE', '10', '-', '-', '-', '10'],
		     ['MORADABAD-MOR', '7', '-', '-', '-', '7'],
		     ['PATNA-PAC', '14', '-', '-', '-', '14'],
		     ['PATNA-PAA', '6', '-', '-', '-', '6'],
		     ['PATNA-PAB', '5', '-', '-', '-', '5'],
		     ['PUNE-PNB', '-', '-', '-', '3', '3'],
		     ['PUNE-PND', '-', '-', '-', '3', '3'],
		     ['PUNE-PNW', '-', '-', '-', '3', '3'],
		     ['JAIPUR-JAA', '-', '-', '5', '-', '5'],
		     ['TOTAL', '126', '4', '5', '8', '143'],
		     ['Rate per employee', '25,000', '25,000', '25,000', '25,000', '25,000'],
		     ['No of days', '30', '28', '7', '5', ''],
		     ['Billing amount Excl ST', '31,50,000', '93,333', '29,167', '33,333', '33,05,833'],
		     ['Service Tax', '3,89,340', '11,536', '3,605', '4,120', '4,08,601'],
		     ['Gross Billing Amount-Manpower', '35,39,340', '1,04,869', '32,772', '37,453', '37,14,434']]
    manpower_table = Table(manpower_data, colWidths=(125, 75, 75, 75, 75, 75))
    manpower_table.setStyle(TableStyle([
	    # aligning the first column
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (0, 1), (0, 1), 'LEFT'),
	    ('ALIGN', (0, 2), (0, 2), 'LEFT'),
	    ('ALIGN', (0, 3), (0, 3), 'LEFT'),
	    ('ALIGN', (0, 4), (0, 4), 'LEFT'),
	    ('ALIGN', (0, 5), (0, 5), 'LEFT'),
	    ('ALIGN', (0, 6), (0, 6), 'LEFT'),
	    ('ALIGN', (0, 7), (0, 7), 'LEFT'),
	    ('ALIGN', (0, 8), (0, 8), 'LEFT'),
	    ('ALIGN', (0, 9), (0, 9), 'LEFT'),
	    ('ALIGN', (0, 10), (0, 10), 'LEFT'),
	    ('ALIGN', (0, 11), (0, 11), 'LEFT'),
	    ('ALIGN', (0, 12), (0, 12), 'LEFT'),
	    ('ALIGN', (0, 13), (0, 13), 'LEFT'),
	    ('ALIGN', (0, 14), (0, 14), 'LEFT'),
	    ('ALIGN', (0, 15), (0, 15), 'LEFT'),
	    ('ALIGN', (0, 16), (0, 16), 'LEFT'),
            ('ALIGN', (0, 17), (0, 17), 'LEFT'),
            ('ALIGN', (0, 18), (0, 18), 'LEFT'),
            ('ALIGN', (0, 19), (0, 19), 'LEFT'),
            ('ALIGN', (0, 20), (0, 20), 'LEFT'),
            ('ALIGN', (0, 21), (0, 21), 'LEFT'),
            ('ALIGN', (0, 22), (0, 22), 'LEFT'),
            ('ALIGN', (0, 23), (0, 23), 'LEFT'),
            ('ALIGN', (0, 24), (0, 24), 'LEFT'),
            ('ALIGN', (0, 25), (0, 25), 'LEFT'),
            ('ALIGN', (0, 26), (0, 26), 'LEFT'),
            ('ALIGN', (0, 27), (0, 27), 'LEFT'),
            ('ALIGN', (0, 28), (0, 28), 'LEFT'),
	    # aligning the headers
	    ('ALIGN', (1, 0), (1, 0), 'CENTER'),
	    ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),
            ('ALIGN', (4, 0), (4, 0), 'CENTER'),
            ('ALIGN', (5, 0), (5, 0), 'CENTER'),
	    # aligning all other to right
	    ('ALIGN', (1, 1), (5, 1), 'RIGHT'),
	    ('ALIGN', (1, 2), (5, 2), 'RIGHT'),
	    ('ALIGN', (1, 3), (5, 3), 'RIGHT'),
	    ('ALIGN', (1, 4), (5, 4), 'RIGHT'),
	    ('ALIGN', (1, 5), (5, 5), 'RIGHT'),
	    ('ALIGN', (1, 6), (5, 6), 'RIGHT'),
	    ('ALIGN', (1, 7), (5, 7), 'RIGHT'),
	    ('ALIGN', (1, 8), (5, 8), 'RIGHT'),
	    ('ALIGN', (1, 9), (5, 9), 'RIGHT'),
	    ('ALIGN', (1, 10), (5, 10), 'RIGHT'),
	    ('ALIGN', (1, 11), (5, 11), 'RIGHT'),
	    ('ALIGN', (1, 12), (5, 12), 'RIGHT'),
	    ('ALIGN', (1, 13), (5, 13), 'RIGHT'),
	    ('ALIGN', (1, 14), (5, 14), 'RIGHT'),
	    ('ALIGN', (1, 15), (5, 15), 'RIGHT'),
	    ('ALIGN', (1, 16), (5, 16), 'RIGHT'),
            ('ALIGN', (1, 17), (5, 17), 'RIGHT'),
            ('ALIGN', (1, 18), (5, 18), 'RIGHT'),
            ('ALIGN', (1, 19), (5, 19), 'RIGHT'),
            ('ALIGN', (1, 20), (5, 20), 'RIGHT'),
            ('ALIGN', (1, 21), (5, 21), 'RIGHT'),
            ('ALIGN', (1, 22), (5, 22), 'RIGHT'),
            ('ALIGN', (1, 23), (5, 23), 'RIGHT'),
            ('ALIGN', (1, 24), (5, 24), 'RIGHT'),
            ('ALIGN', (1, 25), (5, 25), 'RIGHT'),
            ('ALIGN', (1, 26), (5, 26), 'RIGHT'),
            ('ALIGN', (1, 27), (5, 27), 'RIGHT'),
            ('ALIGN', (1, 28), (5, 28), 'RIGHT'),
	    # other aligning
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(manpower_table)

    # first page footer
    def myFirstPage(canvas, doc):
        Title = "Hello world"
        canvas.saveState()
	img_data = '''
               <para>
               <img src="%s" width="84" height="35" valign="0"/><br/>
               </para>''' % img_location
        img = Paragraph(img_data, styles['Normal'])
        #canvas.setFont('Times-Bold',16)
	#canvas.drawCentredString(img, inch, PAGE_HEIGHT - 2 * inch)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "")
        canvas.restoreState()
        
    # later page footer
    def myLaterPages(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        footer_para = '''
<para>
<b>ECOM EXPRESS PRIVATE LIMITED</b></br>
Corporate Office:14/12/2,Samalka,Old Delhi-Gurgaon Road,New Delhi-110037(INDIA)</br>
Registered Office:C-509,Vardhaman Apartments,Plot No.3,Mayur Vihar Phase-I Extension,Delhi-110091(INDIA)</br>
CIN:U63000DL2012PTC241107|Tel.:+911130212000|www.ecomexpress.in
</para>
'''
        P = Paragraph(footer_para, styles['footer'])
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()
    
    # building the document
    doc.build(elements, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    return full_file_name


