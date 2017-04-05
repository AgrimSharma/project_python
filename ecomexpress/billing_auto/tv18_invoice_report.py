from reportlab.lib import colors
from reportlab.lib.units import mm, inch
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
styles.add(ParagraphStyle(name='CenterHeading',
                          alignment=TA_CENTER,
                          fontSize=10))
styles.add(ParagraphStyle(name='bold_right',
                           alignment=TA_RIGHT,
                           fontSize=10))
styles.add(ParagraphStyle(name='bold_left',
                            alignment=TA_LEFT,
                            fontSize=10))
styles.add(ParagraphStyle(name='bold_last',
                            alignment=TA_CENTER,
                            fontSize=8))
styles.add(ParagraphStyle(name='invoice',
                             alignment=TA_CENTER,
                             fontSize=12))
styles.add(ParagraphStyle(name='footer',
                              #alignment=TA_CENTER,
                              fontSize=6))
styles.add(ParagraphStyle(name='image',
                               alignment=TA_RIGHT,
                               fontSize=8))


def generate_invoice_pdf(bill_id, with_header=True):
    print '5.1.1 start generating pdfs for bill ...',bill_id
    billing = Billing.objects.get(id=bill_id)
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
	    71237<br/>
	    DENTSPLY INDIA PRIVATE LIMITED<br/>
	    PLOT NO.358<br/>
	    FIES PATPARGANJ<br/>
	    INDUSTRIAL AREA<br/>
	    DELHI-110092<br/>
	    NOIDA UTTERPRADESH<br/>
	    Phone No: 011-47529683
	    </para>
	    '''

    address_para = Paragraph(para, styles['Normal'])
    table_data = [['Invoice number', '1284'],
	          ['Date', '1-July-2014']]
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
	    services provided in the month of JUNE 2014 at various cities as per list enclosed
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
	    Manpower-90@Rs.25,000 (Location wise detail<br/>
	    attached in annexure)
	    </para>
	    '''
    manpower = Paragraph(manpower_para, styles['Normal'])
    particular_data = [[Paragraph('''<para><b>Sl. No.</b></para>''', styles['CenterHeading']), Paragraph('''<para><b>Particulars</b></para>''', styles['CenterHeading']), Paragraph('''<para><b>Amount</b></para>''', styles['CenterHeading'])],
		       ['1', manpower, '2,250,000.00'],
		       ['2', 'Line Haul charges as per detail attached in annexure', '886,867'],
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
        Paragraph('''<para><b>3,136,867.00</b></para>''', styles['bold_right'])]], 
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
    cess_data = [['', 'Service Tax', '12.00%', '376,424.04'],
	         ['', 'Education Cess', '2.00%', '7,528.48'],
	         ['', 'HSE Cess', '1.00%', '3764.24']]
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
        Paragraph('''<para><b>3,524,584</b></para>''', styles['bold_right'])]], colWidths=(350, 100))
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
	    Rs. Thirty Five Lakh Twenty Four Thousand Five Hundred Eighty Four<br/>
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
    elements.append(Spacer(1, 12))
    
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
    
    # Account head
    account_data = [[
        Paragraph('''<para><b>Account Head</b></para>''', styles['CenterHeading']),
        Paragraph('''<para><b>Billing amount excl ST</b></para>''', styles['CenterHeading']),
        Paragraph('''<para><b>Service Tax</b></para>''', styles['CenterHeading']),
        Paragraph('''<para><b>Total</b></para>''', styles['CenterHeading'])
        ],
        ['Employees', '2,250,000', '278,100', '2,528,100'],
        ['Line Haul', '886,867', '109,617', '996,484'],
        ['Total', '3,136,867', '387,717', '3,524,584']
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
    elements.append(Spacer(1, 624))
    
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
    
    
    # Annexure of Manpower
    single_data = Paragraph('''<para><b>Annexure of Manpower</b></para>''', styles['Normal'])
    single_table = Table([[single_data, '', '']], colWidths=(250, 100, 100))
    single_table.setStyle(TableStyle([
	    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
	    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
	    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.append(single_table)
    
    manpower_data = [[Paragraph('''<para><b>Pick up-Origin</b></para>''', styles['CenterHeading']), Paragraph('''<para><b>16-Feb-2014</b></para>''', styles['CenterHeading']), Paragraph('''<para><b>15-Apr-2014</b></para>''', styles['CenterHeading']), Paragraph('''<para><b>1-May-2014</b></para>''', styles['CenterHeading']), Paragraph('''<para><b>TOTAL</b></para>''', styles['CenterHeading'])],
		     ['PATNA', '10', '6', '', '16'],
		     ['AGRA', '-', '11', '', '11'],
		     ['BIKANER', '-', '8', '', '8'],
		     ['JODHPUR', '-', '8', '', '8'],
		     ['MORADABAD', '-', '7', '', '7'],
		     ['MEERUT', '-', '7', '', '7'],
		     ['GWALIOR', '-', '6', '', '6'],
		     ['LUCKNOW', '-', '6', '', '6'],
		     ['DELHI-DSW', '-', '10', '', '10'],
		     ['DELHI', '-', '-', '11', '11'],
		     ['TOTAL', '10', '69', '11', '90'],
		     ['Rate per employee', '25,000', '25,000', '25,000', '25,000'],
		     ['No of days', '31', '31', '31', '31'],
		     ['Billing amount Excl ST', '250,000', '1,725,000', '275,000', '2,250,000'],
		     ['Service Tax', '30,900', '213,210', '33,990', '278,100'],
		     ['Gross Billing Amount-Manpower', '280,900', '1,938,210', '308,990', '2,528,100']]
    manpower_table = Table(manpower_data, colWidths=(190, 90, 90, 90, 90))
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
	    # aligning the headers
	    ('ALIGN', (1, 0), (1, 0), 'CENTER'),
	    ('ALIGN', (2, 0), (2, 0), 'CENTER'),
	    ('ALIGN', (3, 0), (3, 0), 'CENTER'),
	    ('ALIGN', (4, 0), (4, 0), 'CENTER'),
	    # aligning all other to right
	    ('ALIGN', (1, 1), (4, 1), 'RIGHT'),
	    ('ALIGN', (1, 2), (4, 2), 'RIGHT'),
	    ('ALIGN', (1, 3), (4, 3), 'RIGHT'),
	    ('ALIGN', (1, 4), (4, 4), 'RIGHT'),
	    ('ALIGN', (1, 5), (4, 5), 'RIGHT'),
	    ('ALIGN', (1, 6), (4, 6), 'RIGHT'),
	    ('ALIGN', (1, 7), (4, 7), 'RIGHT'),
	    ('ALIGN', (1, 8), (4, 8), 'RIGHT'),
	    ('ALIGN', (1, 9), (4, 9), 'RIGHT'),
	    ('ALIGN', (1, 10), (4, 10), 'RIGHT'),
	    ('ALIGN', (1, 11), (4, 11), 'RIGHT'),
	    ('ALIGN', (1, 12), (4, 12), 'RIGHT'),
	    ('ALIGN', (1, 13), (4, 13), 'RIGHT'),
	    ('ALIGN', (1, 14), (4, 14), 'RIGHT'),
	    ('ALIGN', (1, 15), (4, 15), 'RIGHT'),
	    ('ALIGN', (1, 16), (4, 16), 'RIGHT'),
	    # other aligning
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(manpower_table)
    """ 
    elements.append(Spacer(1, 384))
    
    # adding logo
    img_data = '''
               <para>
               <img src="%s" width="84" height="35" valign="0"/><br/>
               </para>''' % img_location
    img = Paragraph(img_data, styles['image'])
    
    # Invoice header
    forthpage_table = Table([['', '', img]], colWidths=(100, 100, 400))
    forthpage_table.setStyle(TableStyle([
         ('ALIGN', (0, 0), (0, 0), 'LEFT'),
         ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
         ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(forthpage_table)
    
    # AWB
    #ebsships = list(billing.shipments.filter(shipext__product__product_name__in=['ebsppd', 'ebscod']).values(
    ebsppd = Product.objects.get(product_name='ebsppd')
    ebscod = Product.objects.get(product_name='ebscod')
    ebsships = list(Shipment.objects.filter(
        shipment_date__range=('2014-06-01', '2014-06-05'), 
        shipext__product__in=[ebsppd, ebscod],
        shipper__id=7).values(
            'airwaybill_number',
            'order_number',
            'rts_status',
            'shipext__original_act_weight',
            'chargeable_weight',
            'pickup__service_centre__center_name',
            'original_dest__center_name',
            'order_price__freight_charge',
            'order_price__fuel_surcharge',
            'order_price__rto_charge',
            'order_price__sdl_charge',
            'order_price__sdd_charge',
            'order_price__valuable_cargo_handling_charge',
            'order_price__to_pay_charge',
            'order_price__reverse_charge',
            'codcharge__cod_charge'
    ))
    header_list = [
        Paragraph('''<para><b>AWB</b></para>''', styles['bold_last']),
        Paragraph('''<para><b>Order No</b></para>''', styles['bold_last']),
        Paragraph('''<para><b>Actual Weight</b></para>''', styles['bold_last']),
        Paragraph('''<para><b>Chargeable Weight</b></para>''', styles['bold_last']),
        Paragraph('''<para><b>Origin</b></para>''', styles['bold_last']),
        Paragraph('''<para><b>Destination</b></para>''', styles['bold_last']),
        Paragraph('''<para><b>Rates</b></para>''', styles['bold_last']),
        Paragraph('''<para><b>Charges</b></para>''', styles['bold_last'])
    ]

    awb_data = []

    for ship in ebsships:
        frt = ship.get('order_price__freight_charge')
        fs = ship.get('order_price__fuel_charge')
        vchc = ship.get('order_price__valuable_cargo_handling_charge')
        to_pay = ship.get('order_price__to_pay_charge')
        rto = ship.get('order_price__rto_charge')
        sdl = ship.get('order_price__sdl_charge')
        sdd = ship.get('order_price__sdd_charge')
        rev = ship.get('order_price__reverse_charge')
        charges = [frt, fs, vchc, to_pay, rto, sdl, sdd, rev]
        chgs = [v if v else 0 for v in charges]

        charge = sum(chgs)
        cod_charge = ship.get('codcharge__cod_charge')
        if not cod_charge:
           cod_charge = 0
        if ship.get('rts_status') == 1:
            total_charge = charge - cod_charge 
        else:
            total_charge = charge + cod_charge

	    awb_data.append([
                ship.get('airwaybill_number'),
                ship.get('order_number'),
                ship.get('shipext__original_act_weight'),
                ship.get('chargeable_weight'),
                ship.get('pickup__service_center__center_name'),
                ship.get('original_dest__center_name'),
                0, total_charge
            ])
    awb_data.insert(0, header_list)
    awb_table = Table(awb_data, colWidths=(50, 50, 75, 100, 100, 100, 50, 50))
    awb_table.setStyle(TableStyle([
            # aligning the first column
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (0, 1), (0, 1), 'LEFT'),
            ('ALIGN', (0, 2), (0, 2), 'LEFT'),
	    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(awb_table)
    """
    
    # first page footer
    def myFirstPage(canvas, doc):
        Title = "Hello world"
        canvas.saveState()
        #canvas.setFont('Times-Bold',16)
        #canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
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
