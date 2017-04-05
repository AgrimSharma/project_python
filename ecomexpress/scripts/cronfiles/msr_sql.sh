#!/bin/sh
rm /tmp/MSR_CUR2014.csv
rm /tmp/MSR_CUR2014tot.csv
mysql -u root --password=e1c2o3m4 << eof

use ecomm;
select 'Air waybill Number','Order Number','type','Product Added On','Chargeable Wt','Collectable Value','Declared Value','Customer Code','Customer','Status','Freight','SDL','SDD','Reverse','Fuel Surcharge','VCHC Charge','To Pay','RTS','COD','Total','Origin','Destination','Orig Dest','RTS','Reverse'

union

select s.airwaybill_number, s.order_number, s.product_type, s.inscan_date, s.chargeable_weight, s.collectable_value, s.declared_value, c.code, c.name, 'active', op.freight_charge, op.sdl_charge, op.sdd_charge, op.reverse_charge, op.fuel_surcharge, op.valuable_cargo_handling_charge, op.to_pay_charge, op.rto_charge, if(s.rts_status=1, -cod.cod_charge, cod_charge), 

if (s.product_type = "cod", (op.freight_charge + op.sdl_charge + op.sdd_charge + op.reverse_charge + op.fuel_surcharge + op.valuable_cargo_handling_charge + op.to_pay_charge + op.rto_charge + if(s.rts_status=1, -cod.cod_charge, cod_charge)), (op.freight_charge + op.sdl_charge + op.sdd_charge + op.reverse_charge + op.fuel_surcharge + op.valuable_cargo_handling_charge + op.to_pay_charge + op.rto_charge )),

psc.center_shortcode, csc.center_shortcode, if(sc.center_shortcode = NULL,csc.center_shortcode,sc.center_shortcode), s.rts_status, s.reverse_pickup

INTO OUTFILE '/tmp/MSR_CUR2014.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'

from service_centre_shipment as s left join service_centre_order_price as op on op.shipment_id = s.id left join service_centre_codcharge as cod on cod.shipment_id = s.id left join customer_customer as c on c.id = s.shipper_id left join pickup_pickupregistration as p on p.id = s.pickup_id left join location_servicecenter sc  on sc.id = s.original_dest_id left join location_servicecenter csc  on csc.id = s.service_centre_id  left join location_servicecenter psc  on psc.id = p.service_centre_id where shipment_date >= "2014-03-01" and shipment_date < CURDATE()  ;

 
select 'Total',count(s.airwaybill_number), '','',round(sum(s.chargeable_weight),2),round(sum(s.collectable_value),2),round(sum(s.declared_value),2),'','','',round(sum(op.freight_charge),2),round(sum(op.sdl_charge),2),round(sum(op.sdd_charge),2),round(sum(op.reverse_charge),2),round(sum(op.fuel_surcharge),2),round(sum(op.valuable_cargo_handling_charge),2), round(sum(op.to_pay_charge),2), round(sum(op.rto_charge),2),round(sum(if(s.rts_status=1, -cod.cod_charge, cod_charge)),2),round(sum(if (s.product_type = "cod", (op.freight_charge + op.sdl_charge + op.sdd_charge + op.reverse_charge + op.fuel_surcharge + op.valuable_cargo_handling_charge + op.to_pay_charge + op.rto_charge + if(s.rts_status=1, -cod.cod_charge, cod_charge)), (op.freight_charge + op.sdl_charge + op.sdd_charge + op.reverse_charge + op.fuel_surcharge + op.valuable_cargo_handling_charge + op.to_pay_charge + op.rto_charge ))),2),'','','','',''

INTO OUTFILE '/tmp/MSR_CUR2014tot.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'

from service_centre_shipment as s left join service_centre_order_price as op on op.shipment_id = s.id left join service_centre_codcharge as cod on cod.shipment_id = s.id where shipment_date >= "2014-03-01" and shipment_date < CURDATE();


eof

cat /tmp/MSR_CUR2014tot.csv >> /tmp/MSR_CUR2014.csv

zip /tmp/MSR_CUR2014.zip /tmp/MSR_CUR2014.csv
mv /tmp/MSR_CUR2014.zip /home/web/ecomm.prtouch.com/ecomexpress/static/uploads/
echo "Please Download MSR from following link  http://billing.ecomexpress.in/static/uploads/MSR_CUR2014.zip " | mailx -s 'Monthly Sales Report' samar@prtouch.com

