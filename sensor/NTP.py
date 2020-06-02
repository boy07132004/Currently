import ntplib as ntp
client = ntp.NTPClient()
res    = client.request('192.168.0.100')
sv_time= res.tx_time

import time
lc_date= time.strftime('%Y/%m/%d',time.localtime(sv_time))
lc_time= time.strftime('%X',time.localtime(sv_time))

import os
os.system(f'sudo date -s "{lc_date} {lc_time}"')
print(lc_date,'++++',lc_time)
