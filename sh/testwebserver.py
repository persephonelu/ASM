#!/usr/bin/env python
#coding=utf8
 
import httplib
 
httpClient = None
 
try:
    httpClient = httplib.HTTPConnection('47.88.28.30', 8888, timeout=60)
    httpClient.request('GET', '/keywordreports?email=chenkexin@youyue-inc.com')
 
    #response是HTTPResponse对象
    response = httpClient.getresponse()
    print response.status
    print response.reason
    print response.read()
except Exception, e:
    print e
finally:
    if httpClient:
        httpClient.close()