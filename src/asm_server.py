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
import web
import logging
import logging.handlers

from httpshandler import HTTPSHandler
from campaigns import CampaignsManagement
from keywords import Keywords
from useracls import UserACLs
from reports import Reports

configPath = "../conf"
certPath = "../cert"
logPath ="../log"

LogFile = logPath + "/appleAdvertisement.log"

handler = logging.handlers.TimedRotatingFileHandler(LogFile, when='H', interval=1,backupCount=0)
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger = logging.getLogger('appleAd')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

cf = ConfigParser.ConfigParser()
cf.read(configPath + "/appleSearchAds.config")
restfulUrl = cf.get("appleapiprefix", "apiprefix")

def createHttpsSession(email):
	#读取账号数据,读取cert字符串和key字符串,以及orgId
	sql = "select sshcert,sshkey,orgId from asm_member where is_delete=0 and email='" + email + "'"
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

urls = ('/hello', 'hello',
	'/campaign','index',
	'/adgroups', 'adgroups',
	'/account', 'account',
	'/keywords', 'adwords',
	'/reports', 'reports',
	'/keywordreports', 'keywordreports',
	'/adgroupreports', 'adgroupreports',
	'/campaignsInfo','campaignsInfo',
	'/adgroupsInfo', 'adgroupsInfo',
	'/keywordsInfo','keywordsInfo')

class hello:
	def GET(self):
		return "hello"

class index:
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu", campaignId=None)

		logger.info("Received user " + form.email + "request to create or update appleAd campaign")

		httpsSession = createHttpsSession(form.email)
		campaignsPath = cf.get("apiservices", "campaigns")
		campaign = CampaignsManagement(campaignsPath, httpsSession, logger)
		result = campaign.query_campaign(form.email, form.campaignId)

		return result

class adgroups:
	def GET(self):
		web.header('Content-Type', 'text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu", adgroupId=None)
		logger.info("Received user " + form.email + "request to create or update appleAd adgroup")
		httpsSession = createHttpsSession(form.email)
		campaignsPath = cf.get("apiservices", "campaigns")
		campaign = CampaignsManagement(campaignsPath, httpsSession, logger)
		result = campaign.query_adgroups(form.email, form.adgroupId)

		return result

class account:
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu")

		logger.info("Received user " + form.email + " request to query account info")

		httpsSession = createHttpsSession(form.email)
		aclsPath = cf.get("apiservices", "acls")
		userACLs = UserACLs(aclsPath, httpsSession, logger)
		result = userACLs.getUserACLs(form.email)

		return result

class adwords:
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu", adgroupId=None)

		logger.info("Received user " + form.email + " request to add or update ad keywords")

		httpsSession = createHttpsSession(form.email)
		wordsPath = cf.get("apiservices", "keywords")
		wordhandler = Keywords(wordsPath, httpsSession, logger)
		if form.adgroupId is not None:
			result = wordhandler.query_keywords(email=form.email, adgroupId=form.adgroupId)
		else:
			result = wordhandler.query_all_targeted_keywords(email=form.email)

		return result

class reports:
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu", campaignId=None, starttime=None, endtime=None)

		logger.info("Received user " + form.email + " request to get campaign report")

		httpsSession = createHttpsSession(form.email)
		reportsPath = cf.get("apiservices", "reports")
		reporthandler = Reports(reportsPath, httpsSession, logger)

		result = reporthandler.query_all_campaigns(email=form.email, campaignId=form.campaignId, starttime=form.starttime, endtime=form.endtime)

		return result

class keywordreports:
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu", adgroupId=None, starttime=None, endtime=None)

		logger.info("Received user " + form.email + " request to get campaign report")

		httpsSession = createHttpsSession(form.email)
		reportsPath = cf.get("apiservices", "reports")
		reporthandler = Reports(reportsPath, httpsSession, logger)
		if form.adgroupId is not None:
			result = reporthandler.queryKeywordsReportByAdgroupId(email=form.email, adgroupId=form.adgroupId, starttime=form.starttime, endtime=form.endtime)
		else:
			result = reporthandler.query_all_keywords(email=form.email, starttime=form.starttime, endtime=form.endtime)

		return result

class adgroupreports:
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu", adgroupId=None, starttime=None, endtime=None)

		logger.info("Received user " + form.email + " request to get adgroup report")

		httpsSession = createHttpsSession(form.email)
		reportsPath = cf.get("apiservices", "reports")
		reporthandler = Reports(reportsPath, httpsSession, logger)
		if form.adgroupId is not None:
			result = reporthandler.queryAdgroupReportById(email=form.email, adgroupId=form.adgroupId, starttime=form.starttime, endtime=form.endtime)
		else:
			result = reporthandler.query_all_adgroups(email=form.email, starttime=form.starttime, endtime=form.endtime)

		return result

class campaignsInfo:
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu")

		logger.info("Received user " + form.email + " request to get all campaigns' information")
		httpsSession = createHttpsSession(form.email)
		campaignsPath = cf.get("apiservices", "campaigns")
		campaign = CampaignsManagement(campaignsPath, httpsSession, logger)
		result = campaign.get_campaign_list()

		return result

class adgroupsInfo:
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu", campaignId=None)

		logger.info("Received user " + form.email + " request to get all adgroups' information of campaignId " + str(form.campaignId))
		httpsSession = createHttpsSession(form.email)
		campaignsPath = cf.get("apiservices", "campaigns")
		campaign = CampaignsManagement(campaignsPath, httpsSession, logger)
		result = campaign.get_adgroups_list(campaignId=form.campaignId)

		return result

class keywordsInfo:
	def GET(self):
		web.header('Content-Type','text/html;charset=UTF-8')
		form = web.input(email="fang.lu@sjsu.edu", adgroupId=None)

		logger.info("Received user " + form.email + " request to get all keywords' information of adgroupId " + str(form.adgroupId))
		httpsSession = createHttpsSession(form.email)
		campaignsPath = cf.get("apiservices", "campaigns")
		campaign = CampaignsManagement(campaignsPath, httpsSession, logger)
		result = campaign.get_all_targetingKeywords_By_adgroupId(adgroupId=form.adgroupId)

		return result

if __name__== "__main__":
	app = web.application(urls,globals())
	app.run()
