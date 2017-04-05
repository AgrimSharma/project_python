from service_centre.models import Connection, ConnectionQueue
from service_centre.general_updates import update_shipment_history


def process_queue():
    queue = ConnectionQueue.objects.filter(status=0)
    for q in queue:
        q.status = 1
        q.save()
        connection = q.connection
        if connection.origin.type == 1:
            status = 26
        else:
            status = 27

        bags = connection.bags.all()
        #print 'bags count ({0})'.format(connection.id,), bags.count()
        for bag in bags:
            shipments = bag.ship_data.all()
            #print 'ships count ({0})'.format(bag.bag_number,), shipments.count()
            for ship in shipments:
                #update shipment hisotry
                #print ship.airwaybill_number
                update_shipment_history(
                    ship, sc=connection.origin, status=status, updated_on=connection.added_on,
                    remarks="Shipment connected to {0}.".format(connection.destination,),
                    employee_code=q.employee)
        q.status = 2
        q.save()
