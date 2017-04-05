from reports.report_api import ReportGenerator
from service_centre.models import CODDeposits

def coddeposit_shipments_report(coddid):
    coddeposit = CODDeposits.objects.get(id=coddid)

    report = ReportGenerator('codd_shipments_{0}.xlsx'.format(coddid))
    report.write_header(('Sl No', 'Airwaybill', 'Collected Amount', 'Pending Amt'))
    ships = coddeposit.cod_shipments.values('airwaybill_number', 'shipext__collected_amount', 'collectable_value')
    
    for ind, ship in enumerate(ships, start=1):
        collectable_value = ship.get('collectable_value')
        collectable_value = collectable_value if collectable_value else 0
        collected_amount = ship.get('shipext__collected_amount')
        collected_amount = collected_amount if collected_amount else 0
        report.write_row([ind, ship.get('airwaybill_number'), collected_amount, collectable_value - collected_amount])
    report.write_row(['Total', '', float(coddeposit.collected_amount), float(coddeposit.total_amount) - float(coddeposit.collected_amount)])
    report.manual_sheet_close()
    return report.file_url
