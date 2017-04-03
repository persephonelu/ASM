#!/usr/bin/env python
#coding=utf-8
import httplib


conn = httplib.HTTPSConnection('api.searchads.apple.com', cert_file='../conf/appbk_api.pem',key_file='../conf/appbk_api.key')
conn.request("GET", "/api/v1/acls")
response = conn.getresponse()
print response.status
print response.reason
print response.read()

conn.close()
