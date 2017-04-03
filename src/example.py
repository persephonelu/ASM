#!/usr/bin/env python
#coding=utf-8
import sys
sys.path.append("./")
import httplib
import sql_appbk
import os
import random
import ConfigParser
import datetime

from httpshandler import HTTPSHandler
from campaigns import CampaignsManagement
from keywords import Keywords

configPath = "../conf"
certPath = "../cert"

cf = ConfigParser.ConfigParser()
cf.read(configPath + "/appleSearchAds.config")
restfulUrl = cf.get("appleapiprefix", "apiprefix")

def createHttpsSession(email):
	#读取账号数据,读取cert字符串和key字符串,以及orgId
	sql = "select sshcert,sshkey,orgId from asm_member where email='" + email + "'"
	result = sql_appbk.mysql_com(sql)

	cert_file_str = result[0]['sshcert']
	key_file_str = result[0]['sshkey']
	org_id = result[0]['orgId'] #部分请求可能需要orgId构建http header

	#随机生成一个字符串,防止多个同时运行时出错误
	rand_str = str(random.randint(0,1000000))

	#cert字符串写入一个文件
	cert_file_name = certPath + "/" + rand_str + ".pem"
	cert_output = open(cert_file_name, 'w')
	cert_output.write(cert_file_str)
	#必须close,否则ssl认证会出问题
	cert_output.close()

	#key字符串写入一个文件
	key_file_name = certPath + "/" + rand_str + ".key"
	key_output = open(key_file_name, 'w')
	key_output.write(key_file_str)
	key_output.close()

	return HTTPSHandler(key_file_name, cert_file_name, restfulUrl);

urls = ('/campaign','index')

class index:   
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu")

		httpsSession = createHttpsSession(email)
		campaignsPath = cf.get("apiservices", "campaigns")
		CampaignsManagement campaignObj = CampaignsManagement(campaignsPath, httpsSession)
		campaignObj.query_campaign(form.email)
		return form.email

if __name__== "__main__":
	app = web.application(urls,globals())
	app.run()