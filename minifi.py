from time import sleep
from math import isnan
import time
import sys
import datetime
import subprocess
import sys
import os
import datetime
import traceback
import math
import base64
import json
from time import gmtime, strftime
import random, string
import psutil
import base64
import uuid
# Importing socket library 
import socket 
from sgp30 import SGP30

sgp30 = SGP30()
sgp30.start_measurement()

external_IP_and_port = ('198.41.0.4', 53)  # a.root-servers.net
socket_family = socket.AF_INET

def IP_address():
        try:
            s = socket.socket(socket_family, socket.SOCK_DGRAM)
            s.connect(external_IP_and_port)
            answer = s.getsockname()
            s.close()
            return answer[0] if answer else None
        except socket.error:
            return None

# Get MAC address of a local interfaces
def psutil_iface(iface):
    # type: (str) -> Optional[str]
    import psutil
    nics = psutil.net_if_addrs()
    if iface in nics:
        nic = nics[iface]
        for i in nic:
            if i.family == psutil.AF_LINK:
                return i.address
# Random Word
def randomword(length):
 return ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()) for i in range(length))

# Fixed
packet_size=3000
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
ipaddress = IP_address()

# Second loop

while True:
	start = time.time()
	uniqueid = 'sgp30_uuid_{0}_{1}'.format(randomword(3),strftime("%Y%m%d%H%M%S",gmtime()))
	uuid2 = '{0}_{1}'.format(strftime("%Y%m%d%H%M%S",gmtime()),uuid.uuid4())
	result = sgp30.get_air_quality()
	end = time.time()
	row = { }

	row['uuid'] =  uniqueid
	row['ipaddress']=ipaddress
	row['runtime'] = str(round(end - start))  
	row['host'] = os.uname()[1]
	row['host_name'] = host_name
	row['macaddress'] = psutil_iface('wlan0')
	row['end'] = '{0}'.format( str(end ))
	row['te'] = '{0}'.format(str(end-start))
	row['systemtime'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
	row['cpu'] = psutil.cpu_percent(interval=1)
	usage = psutil.disk_usage("/")
	row['diskusage'] = "{:.1f} MB".format(float(usage.free) / 1024 / 1024)
	row['memory'] = psutil.virtual_memory().percent

	# Equivalent C02: {:5d} (ppm)
	# Total VOC:      {:5d} (ppb)
	row['equivalentco2ppm'] = '{:5d}'.format( (result.equivalent_co2))
	row['totalvocppb'] = '{:5d}'.format( (result.total_voc))
	row['id'] = str(uuid2)
	json_string = json.dumps(row)
	# need this for sensor run that at startup with cron
	# @reboot sleep 300 && /home/wwwjobs/clean-static-cache.sh
	fa=open("/opt/demo/logs/sgp30.log", "a+")
	fa.write(json_string + "\n")
	fa.close()

	time.sleep(1.0)
