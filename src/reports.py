#!/usr/bin/env python
#coding=utf-8
import sys
import httpshandler
import json
import sql_appbk
import datetime
import logging
import MySQLdb

class Reports:
	path = None
	httpshandler = None
	logger = None

	def __init__(self, path, httpshandler, logger):
		self.path = path
		self.httpshandler = httpshandler
		self.logger = logger

	def query_all_campaigns(self, email, campaignId, starttime, endtime):
		status = {}
		status['status'] = 0;
		status['msg'] = "Success!"

		result = None
		try:
			sql_com = ''
			if campaignId is not None:
				sql_com = "select id from asm_campaign where localstat=1 and displayStatus=\"running\" and email=\"" + email + "\" and auto_id=" + str(campaignId)
			else:
				sql_com = "select id from asm_campaign where localstat=1 and displayStatus=\"running\" and email=\"" + email + "\""
			campaigns = sql_appbk.mysql_com(sql_com)

			for campaign in campaigns:
				response = self.get_campaign_report(campaign['id'], starttime, endtime)
				responseData = response.read()
				if response.status != 200:
					status['status'] = -1
					status['msg'] = response.reason
					status['error'] = json.loads(responseData)['error']
					self.logger.error("User " + email + ": get campaign reports Error")
					return json.dumps(status)
				campaignReportJson = json.loads(responseData)['data']
				result = self.saveCampaignReports(campaignReportJson, starttime)
		except Exception,e:
			self.logger.error("User " + email + ": get campaign report failed")
			self.logger.error("Exception : " + str(e))
			status['status'] = -1
			status['msg'] = "Exception occurred!"
		return status
		#return json.dumps(status);
	def query_all_keywords(self, email, starttime, endtime):
		status = {}
		status['status'] = 0;
		status['msg'] = "Success!"

		result = None
		try: 
			sql_com = "select id from asm_campaign where localstat=1 and displayStatus=\"running\" and email=\"" + email + "\""
			campaigns = sql_appbk.mysql_com(sql_com)

			for campaign in campaigns:
				sql_com = "select id from asm_targeted_keywords where localstat=1 and status=\"ACTIVE\" and campaignId=\"" + campaign['id'] + "\""
				keywords = sql_appbk.mysql_com(sql_com)
				for keyword in keywords:
					response = self.get_keyword_report(keyword['id'], campaign['id'], starttime, endtime)
					responseData = response.read()
					if response.status != 200:
						status['status'] = -1
						status['msg'] = response.reason
						status['error'] = json.loads(responseData)['error']
						self.logger.error("User " + email + ": get keyword reports Error")
						return json.dumps(status)
					keywordReportJson = json.loads(responseData)['data']
					#print keywordReportJson
					result = self.saveKeywordsReports(keywordReportJson,starttime)
					#result = self.saveCampaignReports(campaignReportJson)
		except Exception,e:
			self.logger.error("User " + email + ": get keyword report failed")
			self.logger.error("Exception : " + str(e))
			status['status'] = -1
			status['msg'] = "Exception occurred!"
		return status

	def queryKeywordsReportByAdgroupId(self, email, adgroupId, starttime, endtime):
		status = {}
		status['status'] = 0;
		status['msg'] = "Success!"

		result = None
		try: 
			sql_com = "select * from asm_targeted_keywords where status=\"ACTIVE\" and localstat=1 and appbk_group_id=" + adgroupId
			keywords = sql_appbk.mysql_com(sql_com)
				
			for keyword in keywords:
				response = self.get_keyword_report(keyword['id'], keyword['campaignId'], starttime, endtime)
				responseData = response.read()
				if response.status != 200:
					status['status'] = -1
					status['msg'] = response.reason
					status['error'] = json.loads(responseData)['error']
					self.logger.error("User " + email + ": get keyword reports Error")
					return json.dumps(status)
				keywordReportJson = json.loads(responseData)['data']
				result = self.saveKeywordsReports(keywordReportJson, starttime)
		except Exception,e:
			self.logger.error("User " + email + ": get keyword report failed")
			self.logger.error("Exception : " + str(e))
			status['status'] = -1
			status['msg'] = "Exception occurred!"
		return status

	def query_all_adgroups(self, email, starttime, endtime):
		status = {}
		status['status'] = 0;
		status['msg'] = "Success!"

		result = None
		try:
			sql_com = "select id, auto_id from asm_campaign where localstat=1 and displayStatus=\"running\" and email=\"" + email + "\""
			campaigns = sql_appbk.mysql_com(sql_com)
			
			for campaign in campaigns:
				
				sql_com = "select * from asm_adgroup where localstat=1 and appbk_campaign_id=" + str(campaign['auto_id'])
				adgroups = sql_appbk.mysql_com(sql_com)
				
				for adgroup in adgroups:
					response = self.get_adgroup_report(adgroup['id'], campaign['id'], starttime, endtime)
					responseData = response.read()
					if response.status != 200:
						status['status'] = -1
						status['msg'] = response.reason
						status['error'] = json.loads(responseData)['error']
						self.logger.error("User " + email + ": get campaign reports Error")
						return json.dumps(status)
					adGroupReportJson = json.loads(responseData)['data']
					#print adGroupReportJson
					result = self.saveAdgroupReports(adGroupReportJson, starttime)
		except Exception,e:
			self.logger.error("User " + email + ": get adgroup report failed")
			self.logger.error("Exception : " + str(e))
			status['status'] = -1
			status['msg'] = "Exception occurred!"
		return status

	def queryAdgroupReportById(self, email, adgroupId, starttime, endtime):
		status = {} 
		status['status'] = 0;
		status['msg'] = "Success!"

		try:
			sql_com = "select * from asm_adgroup where localstat=1 and auto_id=" + adgroupId
			adgroups = sql_appbk.mysql_com(sql_com)
			
			for adgroup in adgroups:
				response = self.get_adgroup_report(adgroup['id'], adgroup['campaignId'], starttime, endtime)
				responseData = response.read()
				if response.status != 200:
					status['status'] = -1
					status['msg'] = response.reason
					status['error'] = json.loads(responseData)['error']
					self.logger.error("User " + email + ": get campaign reports Error")
					return json.dumps(status)
				adGroupReportJson = json.loads(responseData)['data']
				result = self.saveAdgroupReports(adGroupReportJson, starttime)
		except Exception,e:
			self.logger.error("User " + email + ": get adgroup report failed")
			self.logger.error("Exception : " + str(e))
			status['status'] = -1
			status['msg'] = "Exception occurred!"
		return status	

	def get_campaign_report(self, campaignId, starttime, endtime):
		reportJson = {}
		today = datetime.datetime.now()
		reportJson['startTime'] = (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		if starttime is not None:
			reportJson['startTime'] = starttime

		reportJson['endTime'] = (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		if endtime is not None:
			reportJson['endTime'] = endtime

		selector = {}
		orderList = []
		orderBy = {}
		orderBy['field'] = "campaignId"
		orderBy['sortOrder'] = "DESCENDING"
		orderList.append(orderBy)
		selector['orderBy'] = orderList

		fields = [];
		fields.append("campaignId")
		fields.append("campaignName")
		fields.append("modificationTime")
		fields.append("totalBudget")
		fields.append("localSpend")
		fields.append("ttr")
		fields.append("avgCPT")
		fields.append("avgCPA")
		fields.append("taps")
		fields.append("impressions")
		fields.append("conversions")
		fields.append("conversionRate")
		fields.append("campaignStatus")
		fields.append("dailyBudget")
		fields.append("adamId")
		fields.append("appName")

		selector['fields'] = fields

		pagination = {}
		pagination['limit'] = str(10)
		pagination['offset'] = str(0)
		selector['pagination'] = pagination

		conditions = []
		condition = {}
		condition['field'] = "campaignId"
		condition['operator'] = "EQUALS"
		campaignIdList = []
		campaignIdList.append(campaignId)
		condition['values'] = campaignIdList
		conditions.append(condition)
		selector['conditions'] = conditions
		reportJson['selector'] = selector;

		reportJson['returnRowTotals'] = "true"
		header = {"Content-type": "application/json"}
		#return json.dumps(reportJson)
		return self.httpshandler.do_post(self.path + "/campaigns", json.dumps(reportJson), header)

	def get_keyword_report(self, keywordId, campaignId, starttime, endtime):
		reportJson = {}
		today = datetime.datetime.now()
		reportJson['startTime'] = (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		if starttime is not None:
			reportJson['startTime'] = starttime

		reportJson['endTime'] = (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		if endtime is not None:
			reportJson['endTime'] = endtime

		selector = {}
		orderList = []
		orderBy = {}
		orderBy['field'] = "keywordId"
		orderBy['sortOrder'] = "DESCENDING"
		orderList.append(orderBy)
		selector['orderBy'] = orderList

		fields = [];

		fields.append("localSpend")
		fields.append("ttr")
		fields.append("avgCPT")
		fields.append("avgCPA")
		fields.append("taps")
		fields.append("impressions")
		fields.append("conversions")
		fields.append("conversionRate")
		fields.append("keywordId")

		selector['fields'] = fields

		conditions = []
		condition = {}
		condition['field'] = "keywordId"
		condition['operator'] = "EQUALS"
		keywordIdList = []
		keywordIdList.append(keywordId)
		condition['values'] = keywordIdList
		conditions.append(condition)
		selector['conditions'] = conditions
		reportJson['selector'] = selector;

		reportJson['returnRowTotals'] = "true"
		header = {"Content-type": "application/json"}
		#return json.dumps(reportJson)
		#print json.dumps(reportJson)
		url = self.path + "/campaigns/" + str(campaignId) + "/keywords"
		#print url
		return self.httpshandler.do_post(url, json.dumps(reportJson), header)

	def get_adgroup_report(self, adGroupId, campaignId, starttime, endtime):
		reportJson = {}
		today = datetime.datetime.now()
		reportJson['startTime'] = (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		if starttime is not None:
			reportJson['startTime'] = starttime

		reportJson['endTime'] = (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		if endtime is not None:
			reportJson['endTime'] = endtime

		selector = {}
		orderList = []
		orderBy = {}
		orderBy['field'] = "adGroupId"
		orderBy['sortOrder'] = "DESCENDING"
		orderList.append(orderBy)
		selector['orderBy'] = orderList

		fields = [];
		fields.append("adGroupName")
		fields.append("modificationTime")
		fields.append("taps")
		fields.append("impressions")
		fields.append("conversions")
		fields.append("localSpend")
		fields.append("ttr")
		fields.append("avgCPT")
		fields.append("avgCPA")	
		
		fields.append("conversionRate")
		fields.append("adGroupStatus")

		selector['fields'] = fields

		pagination = {}
		pagination['limit'] = str(10)
		pagination['offset'] = str(0)
		selector['pagination'] = pagination

		conditions = []
		condition = {}
		condition['field'] = "adGroupId"
		condition['operator'] = "EQUALS"
		adGroupIdList = []
		adGroupIdList.append(adGroupId)
		condition['values'] = adGroupIdList
		conditions.append(condition)
		selector['conditions'] = conditions
		reportJson['selector'] = selector;

		reportJson['returnRowTotals'] = "true"
		header = {"Content-type": "application/json"}
		#return json.dumps(reportJson)
		#campaigns/12049183/adgroups
		url = self.path + "/campaigns/" + str(campaignId) + "/adgroups"
		#print json.dumps(reportJson)
		return self.httpshandler.do_post(url , json.dumps(reportJson), header)

	def saveCampaignReports(self, reportJson, starttime=None):
		reportData = reportJson['reportingDataResponse']['row'][0]
		today = datetime.datetime.now()
		totalData = reportData['total']
		metaData  = reportData['metadata']

		report = {};

		report['campaignId'] 	= metaData['campaignId']
		report['localSpend'] 	= totalData['localSpend']['amount']
		report['ttr'] 			= totalData['ttr']
		report['avgCPT'] 		= totalData['avgCPT']['amount']
		report['avgCPA'] 		= totalData['avgCPA']['amount']
		report['taps'] 			= totalData['taps']
		report['impressions'] 	= totalData['impressions']
		report['conversions'] 	= totalData['conversions']
		report['conversionRate'] = totalData['conversionRate']
		report['dailyBudget'] 	= str(0.0)
		if metaData['dailyBudget'] is not None:
			report['dailyBudget'] = metaData['dailyBudget']['amount']
		report['appName']		= metaData['app']['appName']
		report['fetch_date']	= (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		if starttime is not None:
			report['fetch_date'] = starttime

		key_str = ''
		key_list = []
		value_list = []

		for item in report:
			key_list.append(item)
			value_list.append("'" + MySQLdb.escape_string(str(report[item])) + "'")

		#sqlcom
		key_str = ",".join(key_list)
		value_sql = ",".join(value_list)

		sql_com = "insert into asm_campaign_reports_daily (" + key_str + ") values (" + value_sql + ") on duplicate key update localSpend=values(localSpend), ttr=values(ttr), avgCPT=values(avgCPT), avgCPA=values(avgCPA), taps=values(taps), impressions=values(impressions), conversions=values(conversions),conversionRate=values(conversionRate), dailyBudget=values(dailyBudget);"
		sql_appbk.mysql_com(sql_com)

		return sql_com

	def saveKeywordsReports(self, reportJson, starttime=None):
		reportData = reportJson['reportingDataResponse']['row'][0]
		today = datetime.datetime.now()
		totalData = reportData['total']
		metaData  = reportData['metadata']

		report = {};

		report['keywordId'] 	= metaData['keywordId']
		report['localSpend'] 	= totalData['localSpend']['amount']
		report['ttr'] 			= totalData['ttr']
		report['avgCPT'] 		= totalData['avgCPT']['amount']
		report['avgCPA'] 		= totalData['avgCPA']['amount']
		report['taps'] 			= totalData['taps']
		report['impressions'] 	= totalData['impressions']
		report['conversions'] 	= totalData['conversions']
		report['conversionRate'] = totalData['conversionRate']
		report['fetch_date']	= (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		if starttime is not None:
			report['fetch_date'] = starttime
		report['bidAmount']		= metaData['bidAmount']['amount']

		key_str = ''
		key_list = []
		value_list = []

		for item in report:
			key_list.append(item)
			value_list.append("'" + MySQLdb.escape_string(str(report[item])) + "'")

		#sqlcom
		key_str = ",".join(key_list)
		value_sql = ",".join(value_list)

		sql_com = "insert into asm_keywords_reports_daily (" + key_str + ") values (" + value_sql + ") on duplicate key update localSpend=values(localSpend), ttr=values(ttr), avgCPT=values(avgCPT), avgCPA=values(avgCPA), taps=values(taps), impressions=values(impressions), conversions=values(conversions),conversionRate=values(conversionRate), bidAmount=values(bidAmount);"
		sql_appbk.mysql_com(sql_com)
		#print sql_com
		return sql_com

	def saveAdgroupReports(self, reportJson, starttime=None):
		reportData = reportJson['reportingDataResponse']['row'][0]
		today = datetime.datetime.now()
		totalData = reportData['total']
		metaData  = reportData['metadata']

		report = {};

		report['adGroupId'] 	= metaData['adGroupId']
		report['localSpend'] 	= totalData['localSpend']['amount']
		report['ttr'] 			= totalData['ttr']
		report['avgCPT'] 		= totalData['avgCPT']['amount']
		report['avgCPA'] 		= totalData['avgCPA']['amount']
		report['taps'] 			= totalData['taps']
		report['impressions'] 	= totalData['impressions']
		report['conversions'] 	= totalData['conversions']
		report['conversionRate'] = totalData['conversionRate']

		report['fetch_date']	= (today + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		if starttime is not None:
			report['fetch_date'] = starttime
		report['cpaGoal']		= metaData['cpaGoal']['amount']
		report['defaultCpcBid'] = metaData['defaultCpcBid']['amount']

		key_str = ''
		key_list = []
		value_list = []

		for item in report:
			key_list.append(item)
			value_list.append("'" + MySQLdb.escape_string(str(report[item])) + "'")

		#sqlcom
		key_str = ",".join(key_list)
		value_sql = ",".join(value_list)

		sql_com = "insert into asm_adgroup_reports_daily (" + key_str + ") values (" + value_sql + ") on duplicate key update localSpend=values(localSpend), ttr=values(ttr), avgCPT=values(avgCPT), avgCPA=values(avgCPA), taps=values(taps), impressions=values(impressions), conversions=values(conversions),conversionRate=values(conversionRate), cpaGoal=values(cpaGoal), defaultCpcBid=values(defaultCpcBid);"
		#print sql_com
		sql_appbk.mysql_com(sql_com)
		
		return sql_com
