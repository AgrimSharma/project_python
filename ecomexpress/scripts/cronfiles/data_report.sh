#!/bin/sh
rm /tmp/DR_2014.csv
mysql -u root --password=e1c2o3m4 << eof

use ecomm;
select 'Air waybill No','type','Item Description','Chargeable Wt','Vol Wt','Collectable Value','Uploaded Origin','Original Dest','Redirected Dest','Customer','Orig Pincode','P/U Date', 'Status', 'Expected Date', 'Remarks', 'Reason Code', 'Misroute', 'Delay Code', 'First SU', 'RTS AWB', 'RTSD on', 'RTS STATUS', 'updated on ','misroute'

union

select s.airwaybill_number, if(s.reverse_pickup = 1, "REV", s.product_type), s.item_description, s.chargeable_weight, s.volumetric_weight, s.collectable_value, org.center_shortcode, if(sc.center_shortcode = NULL,csc.center_shortcode,sc.center_shortcode), if(sc.center_shortcode = NULL,csc.center_shortcode,sc.center_shortcode), c.name, se.original_pincode, s.added_on, CASE se.status_bk WHEN '0' Then 'Shipment Uploaded' WHEN '1' THEN 'Pickup Complete / Inscan' WHEN '2' THEN 'Inscan completion / Ready for Bagging' WHEN'3' THEN 'Bagging completed' WHEN '4' THEN 'Shipment at HUB' WHEN '5' THEN 'Bagging completed at Hub' WHEN '6' THEN 'Shipment at Delivery Centre' WHEN '7' THEN 'Outscan' WHEN '8' THEN 'Undelivered' WHEN '9' THEN 'Delivered / Closed' WHEN '11' THEN 'alternate instruction' WHEN '12' THEN 'complaint' WHEN '13' THEN 'Assigned to Run Code' WHEN '14' THEN 'Airport Confirmation Sucessfull, connected to destination via Service Centre' WHEN '15' THEN 'Airport Confirmation Successfull, connected to destination via Hub' WHEN '16' THEN 'comments' WHEN '17' THEN 'return' ELSE 'In Transit' END as stat, se.orig_expected_dod, if(s.status = 9, "Delivered", se.remarks), rs.code, ms.code, dl.code, '',s.ref_airwaybill_number, rts.added_on, CASE se_rts.status_bk WHEN '0' Then 'Shipment Uploaded' WHEN '1' THEN 'Pickup Complete / Inscan' WHEN '2' THEN 'Inscan completion / Ready for Bagging' WHEN'3' THEN 'Bagging completed' WHEN '4' THEN 'Shipment at HUB' WHEN '5' THEN 'Bagging completed at Hub' WHEN '6' THEN 'Shipment at Delivery Centre' WHEN '7' THEN 'Outscan' WHEN '8' THEN 'Undelivered' WHEN '9' THEN 'Delivered / Closed' WHEN '11' THEN 'alternate instruction' WHEN '12' THEN 'complaint' WHEN '13' THEN 'Assigned to Run Code' WHEN '14' THEN 'Airport Confirmation Sucessfull, connected to destination via Service Centre' WHEN '15' THEN 'Airport Confirmation Successfull, connected to destination via Hub' WHEN '16' THEN 'comments' WHEN '17' THEN 'return' ELSE '' END as rts_stat, rts.updated_on, rts_misroute.code 

INTO OUTFILE '/tmp/DR_2014.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'

from service_centre_shipment as s left join customer_customer as c on c.id = s.shipper_id left join location_servicecenter sc on sc.id = s.original_dest_id left join location_servicecenter csc  on csc.id = s.service_centre_id left join service_centre_shipmentextension se on se.shipment_id = s.id left join location_servicecenter org on org.id = se.origin_id left join ecomm_admin_shipmentstatusmaster rs on rs.id = s.reason_code_id left join ecomm_admin_shipmentstatusmaster ms on ms.id = se.misroute_code_id left join ecomm_admin_shipmentstatusmaster dl on dl.id = se.delay_code_id left join service_centre_shipment as rts on rts.airwaybill_number = s.ref_airwaybill_number  left join service_centre_shipmentextension se_rts on se.shipment_id = rts.id left join ecomm_admin_shipmentstatusmaster rts_misroute on rts_misroute.id = se_rts.misroute_code_id where s.added_on >= "2014-01-01" and s.added_on < CURDATE();

eof
cd /tmp/
zip DR_2014.zip DR_2014.csv
mv /tmp/DR_2014.zip /home/web/ecomm.prtouch.com/ecomexpress/static/uploads/
echo "Please Download Data Report from following link  http://billing.ecomexpress.in/static/uploads/DR_2014.zip " | mailx -s 'Data Report' samar@prtouch.com

