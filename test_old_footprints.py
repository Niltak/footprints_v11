import base64
from footprintsapi import Footprints as foot
import footprints_v11
import kat_commands as ks
import aa_global as kat
import requests


base_url = 'https://support.purdue.edu/MRcgi/MRWebServices.pl'

# attributes = {
#   "client_id": kat.user,
#   "client_secret": base64.b85decode(kat.pwd()).decode('utf-8'),
#   "base_url": base_url
# }
# test = foot(**attributes)

# test = footprints.Connection(
#     kat.user,
#     'https://support.purdue.edu/MRcgi/MRWebServices.pl',
#     password=base64.b85decode(kat.pwd()).decode('utf-8'))

pwd = base64.b85decode(kat.pwd()).decode('utf-8')
project_id = 17
issue_id = 1637914

payload = f'''
<SOAP-ENV:Envelope 
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" 
  xmlns:namesp2="http://xml.apache.org/xml-soap" 
  xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
    <SOAP-ENV:Header/>
    <SOAP-ENV:Body> 
        <namesp1:MRWebServices__getIssueDetails xmlns:namesp1="MRWebServices">
            <user xsi:type="xsd:string">{kat.user}</user> 
            <password xsi:type="xsd:string">{pwd}</password> 
            <extrainfo xsi:type="xsd:string"/> 
            <projectnumber xsi:type="xsd:int">{project_id}</projectnumber> 
            <mrid xsi:type="xsd:int">{issue_id}</mrid> 
        </namesp1:MRWebServices__getIssueDetails> 
    </SOAP-ENV:Body> 
</SOAP-ENV:Envelope>
'''
data = payload.encode('utf-8')
headers = {
    "SOAPAction" : "MRWebServices#MRWebServices__getIssueDetails",
    "Content-Type" : 'text/xml; charset=utf-8',
    "Content-Length" : "%d" % len(data)
}
response = requests.request("POST", base_url, headers=headers, data=data)

pass