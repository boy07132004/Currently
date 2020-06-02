# Currently


When CT value over threshold, the Raspberry Pi (OPC UA server) will record the vibration values until the CT value is lower than threshold value.   
Then, PC (OPC UA client) will collect the vibration values and save as a csv file.

20200602:
If you want to continuous record data without considering CT values, set CT threshold to 1 and it will update data_list every 2 minutes.

---
### Ref  
Windows as a NTP server: 
https://suntargets.com/windows-%E8%A8%AD%E5%AE%9A%E7%82%BAntp-server/
