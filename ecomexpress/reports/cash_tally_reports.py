import datetime
from django.db.models import Q, Sum
from service_centre.models import CODDeposits
from location.models import ServiceCenter
from reports.report_api import CSVReportGenerator, ReportGenerator


def get_daily_cash_tally_report(from_date, to_date, sc):
    q = Q()
    if from_date and to_date:
        q = q & Q(date__range=(from_date, to_date))
    if int(sc):
        q = q & Q(origin=sc)

    coddeposits = CODDeposits.objects.filter(q).values_list(
        'deposited_on',
        'origin__center_name',
        'total_amount',
        'collected_amount',
        'date',
        'codd_code',
        'slip_number',
        'status')
    col_heads = [
        'COD Delivered date',
        'DC Name',
        'COD Delivered Due Amount',
        'Cash Deposited',
        'Cash Deposited Date',
        'CODID No',
        'Manual Slip No',
        'Short/Excess',
        'Cash Closed Status'
    ]

    file_name = 'daily_cash_tally_report_{0}.xlsx'.format(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M'))
    report = ReportGenerator(file_name)
    report.write_header(col_heads)

    for c in coddeposits:
        collected = c[3] if c[3] else 0
        total = c[2] if c[2] else 0
        short = total - collected
        cash_closed = 'yes' if int(c[7]) == 1 else 'no'
        row_data = [c[0], c[1], c[2], c[3], c[4], c[5], c[6], short, cash_closed]
        report.write_row(row_data)
    report.manual_sheet_close()
    return file_name

def scwise_daily_cash_tally_report(from_date, to_date, sc):
    if from_date and to_date:
        start_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
    if int(sc):
        sc_list = ServiceCenter.objects.filter(id=sc)
    else:
        sc_list = ServiceCenter.objects.all()
    delta = end_date - start_date
    days = [start_date + datetime.timedelta(days=d) for d in range(delta.days + 1)]

    col_heads = [
        'COD Delivered date',
        'DC Name',
        'COD Delivered Due Amount',
        'Cash Deposited',
        'Cash Deposited Date',
        'CODID No',
        'Manual Slip No',
        'Short/Excess',
        'Cash Closed Status'
    ]
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    report = ReportGenerator('scwise_daily_cash_tally_report_{0}.xlsx'.format(now))
    report.write_row(col_heads)

    for day in days:
        for sc in sc_list:
            cd = CODDeposits.objects.filter(origin=sc, date=day)
            if cd:
                cod_id_list = list(cd.values_list('codd_code', flat=True))
                sliplist = list(cd.values_list('slip_number', flat=True))
                delivered_dates = list(cd.values_list('deposited_on', flat=True))

                codids = [c for c in cod_id_list if c]
                slip_list = [s for s in sliplist if s]
                del_dates = [d.strftime('%Y-%m-%d') for d in delivered_dates if d]

                amt_dict = cd.aggregate(tot_amt=Sum('total_amount'), tot_coll=Sum('collected_amount'))
                cod_ids = ', '.join(codids)
                slip_nums = ', '.join(slip_list)
                deldates = ', '.join(del_dates)
            else:
                amt_dict = {}
                cod_ids = ''
                slip_nums = ''
                deldates = ''
            total_amount = amt_dict.get('tot_amt')
            deposit_amount = amt_dict.get('tot_coll')
            total_amount = total_amount if total_amount else 0
            deposit_amount = deposit_amount if deposit_amount else 0
            short = total_amount - deposit_amount
            cash_status = 'no' if abs(short) > 20  else 'yes'
            cod_del_date = day.strftime('%Y-%m-%d')
            row_data = [
                cod_del_date,
                sc.center_name,
                total_amount,
                deposit_amount,
                deldates,
                cod_ids,
                slip_nums,
                short,
                cash_status
            ]
            report.write_row(row_data)
    return report.file_name
