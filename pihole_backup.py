#pihole backup
'''
# pihole_backup.py
# created by mahemys; 2023.07.22 18:40 IST
# !perfect, but works!
# GNU-GPL; no license; free to use!
# update 2023-07-24 10:15 IST; initial review; optimise
# update 2023-07-25 21:50 IST; refer api endpoints
#
#------------------------------------------------------------
# purpose
# pihole perform internal routine and backup of database and configuration to archive
#
# pihole database will grow over time; move db to archive
# pihole perform internal routine; backup config to archive
# internal log writing; time in ist;
#
#------------------------------------------------------------
# how to use
# just copy file to pihole /home/pi/
# run this python script in terminal or via crontab
#
# terminal
# run in terminal "sudo python3 /home/pi/pihole_backup.py"
#
#------------------------------------------------------------
# crontab
# user pi; root not required
# crontab -e edit; crontab -l check
# set your desired interval via crontab preferred e.o.d 23:59
# add to crontab  "59 23 * * * sudo python3 /home/pi/pihole_backup.py"
#
#------------------------------------------------------------
# requirements
# pytz for timezone
# sudo apt-get install python3-pip
# sudo pip install pytz
#
#------------------------------------------------------------
# process
# get stats -> stop ftl -> backup db -> start ftl -> backup config -> flush -> update
#
# 0.0 pihole version; stats
# 0.1 get pihole version
# 0.2 get pihole stats
#
# 1.0 pihole move db to archive
# 1.1 pihole folder
# 1.2 stop FTL service
# 1.3 get file size
# 1.4 folder name
# 1.5 move to folder; rename
# 1.6 start FTL service
#
# 2.0 pihole perform internal routine
# 2.1 backup configuration
# 2.2 flush pihole.log
# 2.3 flush network table
# 2.4 update gravity aka adlist
# 2.5 update pi-hole aka all
#
#------------------------------------------------------------
# pihole folders; files
#
# pihole folder  /etc/pihole/
# pihole ftl db  /etc/pihole/pihole-FTL.db
#
# archive  /home/pi/pihole_bkp/
# database /home/pi/pihole_bkp/Y/Ym/pihole-FTL_Ymd_HMS.db
# config   /home/pi/pihole_bkp/Y/Ym/pihole-conf_Ymd_HMS.tar.gz
# bkplog   /home/pi/pihole_bkp/Y/Ym/pihole_bkp_log_Ymd_HMS.txt
#
#------------------------------------------------------------
# pihole useful commands
#
# pihole -v        display version of each service
# pihole -v -a     display version of AdminLTE
# pihole -v -f     display version of FTL
# pihole -v -p     display version of pi-hole
# pihole -a -t     backup config teleporter to archive
# pihole -f        flush pihole.log
# pihole arpflush  flush network table
# pihole -g        update gravity aka adlist
# pihole -up       update pihole version
#
#------------------------------------------------------------
# tweak to get stats without login
#
# get stats from /pihole instead of /admin
# keep old version of pi-hole 'AdminLTE v5.13' in /home/pi/AdminLTE-5.13
# copy entire 'AdminLTE-5.13' folder to /var/www/html/pihole
#
# sudo cp -a /home/pi/AdminLTE-5.13/. /var/www/html/pihole
#
# AdminLTE v5.13 and below -> /var/www/html/pihole -> no login required
# AdminLTE v5.14 and above -> /var/www/html/admin  -> login or API Token required
#
#------------------------------------------------------------
# authentication for more API endpoints required
#
# in order to avoid the above; follow the below!
# https://discourse.pi-hole.net/t/upcoming-changes-authentication-for-more-api-endpoints-required/59315
# https://pi-hole.net/blog/2022/11/17/upcoming-changes-authentication-for-more-api-endpoints-required/#page-content
#
# You can get the token from Settings/API/Show API token or from /etc/pihole/setupVars.conf (WEBPASSWORD).
# /admin/api.php?summaryRaw
# /admin/api.php?summaryRaw&auth=<TOKEN>
#
#------------------------------------------------------------
'''
#permissions
pihole_api_token   = "";   #api token
pihole_bkp_ftl_db  = 'yes' #yes; no
pihole_bkp_config  = 'yes' #yes; no
config_backup_tele = 'yes' #yes; no
config_flush_logs  = 'yes' #yes; no
config_flush_netw  = 'yes' #yes; no
config_update_grvt = 'yes' #yes; no
config_update_pih  = 'no'  #yes; no

import os
import platform
import requests
import time, pytz
from datetime import datetime

#time zone of specified location
timezone   = 'Asia/Kolkata'
IST        = pytz.timezone(timezone)
dt_start   = datetime.now(IST)
python_ver = platform.python_version()

print(" ", dt_start, 'start...')
print(" ", "python version - ", python_ver)

#date time
datetime_ist    = datetime.now(IST)
LogDateYearIST  = datetime_ist.strftime('%Y')
LogDateMonthIST = datetime_ist.strftime('%m')
LogDateDayIST   = datetime_ist.strftime('%d')
LogDateTimeIST  = datetime_ist.strftime('%Y%m%d_%H%M%S')

#logs folders; files
Folder_Main    = 'pihole_bkp'
Folder_YYYY    = LogDateYearIST
Folder_YYYYMM  = LogDateYearIST + LogDateMonthIST
logs_file_name = Folder_Main + "_log_" + LogDateTimeIST + ".txt"

try:
    #logs folders; files
    File_path    = os.path.abspath(__file__)
    File_dir     = os.path.dirname(__file__)
    Logs_dir     = os.path.join(File_dir, Folder_Main)
    Logs_dir_yr  = os.path.join(Logs_dir, Folder_YYYY)
    Logs_dir_cur = os.path.join(Logs_dir_yr, Folder_YYYYMM)
    
    #create folders if not found
    if not os.path.isdir(Logs_dir):
        os.makedirs(Logs_dir)
    if not os.path.isdir(Logs_dir_yr):
        os.makedirs(Logs_dir_yr)
    if not os.path.isdir(Logs_dir_cur):
        os.makedirs(Logs_dir_cur)
    logs_file_name = os.path.join(Logs_dir_cur, logs_file_name)
except:
    print(" ", '#Exception: create folders', logs_file_name)
    pass

#logs save as text file
text_file = open(logs_file_name, "w")
text_file.write(logs_file_name + '\n')
text_file.write('\n')
text_file.write("python version - {}".format(python_ver) + '\n')
text_file.write('\n')

#pihole folders; files
pihole_folder   = "/etc/pihole/"
pih_db_name_old = "pihole-FTL.db"
pih_db_name_new = "pihole-FTL"   + "_" + LogDateTimeIST + ".db"
pih_name_config = "pihole-config"+ "_" + LogDateTimeIST + ".tar.gz"
pih_db_dest_old = pihole_folder  + "/" + pih_db_name_old
pih_db_dest_new = Logs_dir_cur   + "/" + pih_db_name_new
pih_dest_config = Logs_dir_cur   + "/" + pih_name_config

#sudo commands; linux; pihole
pih_cd_folder = "cd /etc/pihole/"
pih_ftl_stop  = "sudo service pihole-FTL stop"
pih_db_move   = "sudo mv " + pih_db_dest_old + " " + pih_db_dest_new
pih_ftl_start = "sudo service pihole-FTL start"

#non sudo commands; pihole
pih_version_chk = "pihole -v"
pih_config_bkp  = "pihole -a -t " + pih_dest_config
pih_flush_logs  = "pihole -f"
pih_flush_netw  = "pihole arpflush"
pih_update_grvt = "pihole -g"
pih_update_pih  = "pihole -up"

def get_size(path):
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024,2):
        return f"{round(size/1024, 2)} KB"
    elif size < pow(1024,3):
        return f"{round(size/(pow(1024,2)), 2)} MB"
    elif size < pow(1024,4):
        return f"{round(size/(pow(1024,3)), 2)} GB"
    
def log_write(instance):
    log_text = "{} {}".format(datetime.now(IST), instance)
    text_file.write(log_text + '\n')
    print(" ", log_text)

def get_pihole_version():
    try:
        #0.1 get pihole version
        pih_ver_pihole   = os.popen("pihole -v -p").read().strip()
        pih_ver_ftl      = os.popen("pihole -v -f").read().strip()
        pih_ver_adminlte = os.popen("pihole -v -a").read().strip()
        
        instance = "pihole -v -p; os response {}".format(pih_ver_pihole)
        log_write(instance)
        
        instance = "pihole -v -f; os response {}".format(pih_ver_ftl)
        log_write(instance)
        
        instance = "pihole -v -a; os response {}".format(pih_ver_adminlte)
        log_write(instance)
    except:
        instance = "#Exception: get pihole version"
        log_write(instance)
        pass

def get_pihole_stats():
    try:
        #0.2 get pihole stats
        instance = "pihole get stats before proceeding"
        log_write(instance)
        
        #refer tweak to get stats without login
        #localhost or local ip assigned by your network to pihole
        www_html_pihole = "/var/www/html/pihole/"
        www_html_admin  = "/var/www/html/admin/"
        if os.path.exists(www_html_pihole):
            #localhost; /pihole
            url_pihole = "http://localhost/pihole/api.php?summaryRaw"
        else:
            #localhost; /admin
            url_pihole = "http://localhost/admin/api.php?summaryRaw&auth="+ pihole_api_token
        
        instance = "pihole url " + url_pihole
        log_write(instance)
        
        url_start  = datetime.now(IST)
        r = requests.get(url_pihole, timeout=5)
        status = r.status_code
        header = r.headers
        reason = r.reason
        r_text = str(r.text)
        #print(" ", r_text)
        
        if r.status_code == 200:
            r_resp = str(r.text)
            #print(" ", r_resp)
        else: 
            r_resp = "empty"
            #print(" ", r_resp)
        
        url_stop = datetime.now(IST)
        url_time = url_stop - url_start
        log_text = "{} pihole resptime {}, status {}, reason {}".format(datetime.now(IST), url_time, status, reason)
        
        text_file.write(log_text + '\n')
        print(" ", log_text)
        
        log_text = r_text.replace(',', ',\n')
        text_file.write('\n' +  log_text + '\n' + '\n')
    except:
        instance = "#Exception: get pihole stats"
        log_write(instance)
        pass

def main_process():
    #check pihole version
    #error code: 0 -> found; 1 -> not found windows; 32512 -> not found linux
    os_resp = os.system("pihole -v")
    print(" ", "pihole -v; os response ", os_resp)
    
    if str(os_resp) != "0":
        instance = "pihole not found; os response {}; skip all processes".format(os_resp)
        log_write(instance)
    else:
        instance = "pihole found; os response {}; continue processes".format(os_resp)
        log_write(instance)

        #0.0 pihole version; stats
        get_pihole_version()
        get_pihole_stats()
        
        #1.0 pihole move db to archive
        if pihole_bkp_ftl_db != 'yes':
            instance = "pihole backup db - no; skip process"
            log_write(instance)
        else:
            instance = "pihole backup db - yes; continue process"
            log_write(instance)
            
            try:
                #1.1 pihole folder
                #os.system(pih_cd_folder)
                instance  = "pihole folder " + pihole_folder
                log_write(instance)
                
                #1.2 stop FTL service
                os.system(pih_ftl_stop)
                instance  = "stop FTL service"
                log_write(instance)
                
                #1.3 get file size
                if os.path.exists(pih_db_dest_old):
                    filesize = get_size(pih_db_dest_old)
                else:
                     filesize = "0"
                instance = "file size; " + pih_db_name_old + "; " + filesize + " bytes"
                log_write(instance)
                
                #1.4 folder name
                instance = "backup folder; " + Logs_dir_cur
                log_write(instance)
                
                #1.5 move to folder; rename
                if os.path.exists(pih_db_dest_old):
                    os.system(pih_db_move)
                    instance = "db move; rename; ok " + pih_db_name_new
                    log_write(instance)
                else:
                    instance = "db file not found; " + pih_db_name_old
                    log_write(instance)
                
                #1.6 start FTL service
                os.system(pih_ftl_start)
                instance = "start FTL service"
                log_write(instance)
                
                #after this a new db will be created by pihole
            except:
                instance = "#Exception: archive db"
                log_write(instance)
                pass
        
        #2.0 pihole perform internal routine
        if pihole_bkp_config != 'yes':
            instance = "pihole backup config - no; skip process"
            log_write(instance)
        else:
            instance = "pihole backup config - yes; continue process"
            log_write(instance)
            
            try:
                #2.1 backup config teleporter
                if config_backup_tele != 'yes':
                    instance = "backup config teleporter - no; skip; " + pih_config_bkp
                else:
                    os.system(pih_config_bkp)
                    instance = "backup config teleporter - yes; continue; " + pih_config_bkp
                log_write(instance)
                
                #2.2 flush pihole.log
                if config_flush_logs != 'yes':
                    instance = "flush pihole.log - no; skip; " + pih_flush_logs
                else:
                    os.system(pih_flush_logs)
                    instance = "flush pihole.log - yes; continue; " + pih_flush_logs
                log_write(instance)
                
                #2.3 flush network table
                if config_flush_netw != 'yes':
                    instance = "flush network table - no; skip; " + pih_flush_netw
                else:
                    os.system(pih_flush_netw)
                    instance = "flush network table - yes; continue; " + pih_flush_netw
                log_write(instance)
                
                #2.4 update gravity
                if config_update_grvt != 'yes':
                    instance = "update gravity - no; skip; " + pih_update_grvt
                else:
                    os.system(pih_update_grvt)
                    instance = "update gravity - yes; continue; " + pih_update_grvt
                log_write(instance)
                
                #2.5 update pi-hole
                if config_update_pih != 'yes':
                    instance = "update pi-hole - no; skip; " + pih_update_pih
                else:
                    os.system(pih_update_pih)
                    instance = "update pi-hole - yes; continue; " + pih_update_pih
                log_write(instance)
            except:
                instance = "#Exception: archive config"
                log_write(instance)
                pass
    
    #print time taken
    dt_stop = datetime.now(IST)
    dt_diff = (dt_stop - dt_start)
    print(" ", dt_stop, 'all tasks complete...')
    print(" ", 'Time taken {}'.format(dt_diff))
    
    text_file.write('\n')
    text_file.write('Time Start : {}'.format(dt_start) + '\n')
    text_file.write('Time Stop  : {}'.format(dt_stop)  + '\n')
    text_file.write('Time Taken : {}'.format(dt_diff)  + '\n')
    text_file.close()
    
if __name__ == "__main__":
   try:
      main_process()
   except KeyboardInterrupt:
      # do nothing here
      text_file.write("{} - KeyboardInterrupt - Exit...".format(datetime.now(IST)) + '\n')
      text_file.close()
      pass
