# pihole backup
- pihole_backup.py
- created by mahemys 2023.07.22 18:40 IST
- !perfect, but works!
- GNU-GPL; no license; free to use!
- update 2023-07-24 10:15 IST; initial review; optimise
- update 2023-07-25 21:50 IST; refer api endpoints
- update 2023-07-26 21:05 IST; get api token from file

**purpose**
- pihole perform internal routine and backup of database and configuration to archive
- pihole database will grow over time; move db to archive
- pihole perform internal routine; backup config to archive
- internal log writing; time in ist;

**how to use**
- just copy file to pihole /home/pi/
- run this python script in terminal or via crontab

**terminal**
- run in terminal "sudo python3 /home/pi/pihole_backup.py"

**crontab**
- user pi; root not required
- crontab -e edit; crontab -l check
- set your desired interval via crontab preferred e.o.d 23:59
- add to crontab  "59 23 * * * sudo python3 /home/pi/pihole_backup.py"

**requirements**
- pytz for timezone
- sudo apt-get install python3-pip
- sudo pip install pytz

**process**
- get stats -> stop ftl -> backup db -> start ftl -> backup config -> flush -> update

**0.0 pihole version; stats; token**
- 0.1 get pihole version
- 0.2 get pihole stats
- 0.3 get pihole api token

**1.0 pihole move db to archive**
- 1.1 pihole folder
- 1.2 stop FTL service
- 1.3 get file size
- 1.4 folder name
- 1.5 move to folder; rename
- 1.6 start FTL service

**2.0 pihole perform internal routine**
- 2.1 backup configuration
- 2.2 flush pihole.log
- 2.3 flush network table
- 2.4 update gravity aka adlist
- 2.5 update pi-hole aka all

**pihole folders; files**
- pihole folder  /etc/pihole/
- pihole ftl db  /etc/pihole/pihole-FTL.db
- archive  /home/pi/pihole_bkp/
- database /home/pi/pihole_bkp/Y/Ym/pihole-FTL_Ymd_HMS.db
- config   /home/pi/pihole_bkp/Y/Ym/pihole-conf_Ymd_HMS.tar.gz
- bkplog   /home/pi/pihole_bkp/Y/Ym/pihole_bkp_log_Ymd_HMS.txt

**pihole useful commands**
- pihole -v        display version of each service
- pihole -v -a     display version of AdminLTE
- pihole -v -f     display version of FTL
- pihole -v -p     display version of pi-hole
- pihole -a -t     backup config teleporter to archive
- pihole -f        flush pihole.log
- pihole arpflush  flush network table
- pihole -g        update gravity aka adlist
- pihole -up       update pihole version

**tweak to get stats without login**
- get stats from /pihole instead of /admin
- keep old version of pi-hole 'AdminLTE v5.13' in /home/pi/AdminLTE-5.13
- copy entire 'AdminLTE-5.13' folder to /var/www/html/pihole
- sudo cp -a /home/pi/AdminLTE-5.13/. /var/www/html/pihole
- AdminLTE v5.13 and below -> /var/www/html/pihole -> no login required
- AdminLTE v5.14 and above -> /var/www/html/admin  -> login or API Token required

**authentication for more API endpoints required**
- in order to avoid the above; follow the below!
- https://discourse.pi-hole.net/t/upcoming-changes-authentication-for-more-api-endpoints-required/59315
- https://pi-hole.net/blog/2022/11/17/upcoming-changes-authentication-for-more-api-endpoints-required/#page-content
- You can get the token from Settings/API/Show API token or from /etc/pihole/setupVars.conf (WEBPASSWORD).
- /admin/api.php?summaryRaw
- /admin/api.php?summaryRaw&auth=\<TOKEN\>

**footnote**
- let me know if you find any bugs!
- Thank you mahemys
