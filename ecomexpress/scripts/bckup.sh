today=`date "+%F-%H-%M"`
#echo "hi"
#mysqldump -uecomm -pecomm --default-character-set=utf8 ecomm  > /mnt/backupdump/$today.sql
echo "hello"
mysqldump -h 10.43.156.203 -uecomm -pecomm --default-character-set=utf8 ecomm  > /mnt/backupdump/compressed_$today.sql
echo "gzip"
/bin/gzip /mnt/backupdump/compressed_$today.sql
echo "done"
/usr/bin/scp -r /mnt/backupdump/compressed_$today.sql.gz  jignesh@i.prtouch.com:ecomm_db_bk/
echo "backedup"
