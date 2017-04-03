#!/usr/bin/env python
#coding=utf-8
import sys
import httpshandler
import json
import sql_appbk
import datetime
import logging

class Keywords:
	path = None
	httpshandler = None
	logger = None

	def __init__(self, path, httpshandler, logger):
		self.path = path
		self.httpshandler = httpshandler
		self.logger = logger

	def query_all_targeted_keywords(self, email):
		status = {}
		status['status'] = 0;
		status['msg'] = "Success!"
		try:
			sql_com = "select id from asm_campaign where displayStatus=\"running\" and email=\"" + email + "\""
			campaigns = sql_appbk.mysql_com(sql_com)

			for campaign in campaigns:
				sql_com = "select * from asm_targeted_keywords where localstat=0 and campaignId=" + campaign['id'] 

				result = sql_appbk.mysql_com(sql_com)
				for ret in result:
					if ret['id'] is not None:
						response = self.update_targeted_keywords(ret)
					
						responseJson = response.read();
						if response.status != 200:
							status['status'] = -1
							status['msg'] = response.reason
							status['error'] = json.loads(responseJson)['error']
							self.logger.error("User " + email + ": update a target keyword " + str(ret['auto_id']) + " Error")
							return json.dumps(status)
						responseJson = json.loads(responseJson)['data']
						
						self.saveTargetedKeywords(responseJson[0], ret['auto_id'])
					else:
						response = self.create_targeted_keywords(ret)
					
						responseJson = response.read();
						if response.status != 200:
							status['status'] = -1
							status['msg'] = response.reason
							status['error'] = json.loads(responseJson)['error']
							self.logger.error("User " + email + ": create a target keyword " + str(ret['auto_id']) + " Error")
							return json.dumps(status)
						responseJson = json.loads(responseJson)['data']
					
						self.saveTargetedKeywords(responseJson[0], ret['auto_id'])
		except Exception,e:
			self.logger.error("User " + email + ": create or update a target keyword " + str(ret['auto_id']) + " failed")
			self.logger.error(Exception + " : " + e)
			status['status'] = -1
			status['msg'] = "Exception occurred!"
		return json.dumps(status);

	def query_keywords(self, email, adgroupId):
		status = {}
		status['status'] = 0;
		status['msg'] = "Success!"
		try:
			sql_com = "select * from asm_targeted_keywords where localstat=0 and appbk_group_id=" + adgroupId
			keywords = sql_appbk.mysql_com(sql_com)
			
			for ret in keywords:
				if ret['id'] is not None:
					response = self.update_targeted_keywords(ret)
					responseJson = response.read();
					if response.status != 200:
						status['status'] = -1
						status['msg'] = response.reason
						status['error'] = json.loads(responseJson)['error']
						self.logger.error("User " + email + ": update a target keyword " + str(ret['auto_id']) + " Error")
						return json.dumps(status)
					responseJson = json.loads(responseJson)['data']
						
					self.saveTargetedKeywords(responseJson[0], ret['auto_id'])
				else:
					response = self.create_targeted_keywords(ret)
					responseJson = response.read();
					if response.status != 200:
						status['status'] = -1
						status['msg'] = response.reason
						status['error'] = json.loads(responseJson)['error']
						self.logger.error("User " + email + ": create a target keyword " + str(ret['auto_id']) + " Error")
						return json.dumps(status)
					responseJson = json.loads(responseJson)['data']
						
					self.saveTargetedKeywords(responseJson[0], ret['auto_id'])
		except Exception,e:
			self.logger.error("User " + email + ": create or update a target keyword " + str(ret['auto_id']) + " failed")
			self.logger.error(Exception + " : " + e)
			status['msg'] = "Exception occurred!"
		return json.dumps(status);

	def create_targeted_keywords(self, keywordJson):
		TargetedKeywords = {}
		TargetedKeywords['importAction'] = "CREATE"
		TargetedKeywords['id'] = None
		TargetedKeywords['text'] = keywordJson['text']
		TargetedKeywords['campaignId'] = keywordJson['campaignId']
		TargetedKeywords['adGroupId'] = keywordJson['adGroupId']
		TargetedKeywords['matchType'] = keywordJson['matchType']

		if keywordJson['status'] is not None:
			TargetedKeywords['status'] = keywordJson['status']
		bidAmount = {}
		bidAmount["amount"] = str(keywordJson['bidAmount'])
		bidAmount["currency"] = "USD" 
		TargetedKeywords["bidAmount"] = bidAmount

		header = {"Content-type": "application/json"}
		jsonlist = []
		jsonlist.append(TargetedKeywords)

		return self.httpshandler.do_post(self.path + "/targeting", json.dumps(jsonlist), header)

	def update_targeted_keywords(self, keywordJson):
		TargetedKeywords = {}
		TargetedKeywords['importAction'] = "UPDATE"
		TargetedKeywords['id'] = str(keywordJson['id'])
		if keywordJson['text'] is not None:
			TargetedKeywords['text'] = keywordJson['text']

		TargetedKeywords['campaignId'] = keywordJson['campaignId']
		TargetedKeywords['adGroupId'] = keywordJson['adGroupId']

		if keywordJson['matchType'] is not None:
			TargetedKeywords['matchType'] = keywordJson['matchType']
		if keywordJson['status'] is not None:
			TargetedKeywords['status'] = keywordJson['status']

		if keywordJson['bidAmount'] is not None:
			bidAmount = {}
			bidAmount["amount"] = str(keywordJson['bidAmount'])
			bidAmount["currency"] = "USD"
			TargetedKeywords["bidAmount"] = bidAmount

		header = {"Content-type": "application/json"}
		jsonlist = []
		jsonlist.append(TargetedKeywords)
		#print json_dumps(jsonlist)
		return self.httpshandler.do_post(self.path + "/targeting", json.dumps(jsonlist), header)

	def find_targeted_keywords(self):
		return self.httpshandler.do_post(self.path)
	
	def find_negative_keywords(self):
		return self.httpshandler.do_post(self.path)

	def create_negative_keywords(self, adGroupId, campaignId, text):
		NegativeKeywords = {}
		NegativeKeywords["importAction"] = "CREATE"
		NegativeKeywords["adGroupId"] = adGroupId
		NegativeKeywords["text"] = text
		NegativeKeywords["campaignId"] = campaignId

		header = {"Content-type": "application/json"}
		jsonlist = []
		jsonlist.append(NegativeKeywords)

		return self.httpshandler.do_post(self.path + "/negative", json.dumps(jsonlist), header)

	def update_negative_keywords(self):
		return self.httpshandler.do_post(self.path)

	def saveTargetedKeywords(self, keywordJson, auto_id):
		keyword = {}
		keyword["id"] = keywordJson['id']
		keyword["adGroupId"] = keywordJson['adGroupId']
		keyword["text"] = keywordJson['text']
		keyword["status"] = keywordJson['status']
		keyword["matchType"] = keywordJson['matchType']
		keyword["bidAmount"]  = keywordJson['bidAmount']['amount']
		keyword['updateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		keyword['localstat'] = 1 

		sql_com = "update asm_targeted_keywords set "
		conditions = [];
		for item in keyword:
			conditions.append(str(item) + "=\"" + str(keyword[item]) + "\"")

		sql_com += " , ".join(conditions)
		sql_com += " where auto_id=" + str(auto_id)
		sql_appbk.mysql_com(sql_com)
		#print sql_com
		return sql_com
if __name__== "__main__":
	id = 81
	ret = query_keywords(id)
	print ret.read()
