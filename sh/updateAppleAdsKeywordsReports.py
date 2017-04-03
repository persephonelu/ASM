#!/usr/bin/env python
#coding=utf-8
import sys
sys.path.append("./")
import sql_appbk
import os
import random
import logging
import logging.handlers
import httplib

httpClient = None

def getUserList():
	sql_com = "select distinct(email) from asm_member where is_delete=0;"
	userlist = sql_appbk.mysql_com(sql_com)
	return userlist

if __name__== "__main__":
	userlist = getUserList()
	try:
		httpClient = httplib.HTTPConnection('47.88.28.30', 8088, timeout=60)
		for email in userlist:
			print email['email']
			path = '/keywordreports?email=' + str(email['email'])
			httpClient.request('GET', path)
			response = httpClient.getresponse()
			print response.status
			print response.reason
			print response.read()
	except Exception, e:
		print e
	finally:
		if httpClient:
			httpClient.close()
