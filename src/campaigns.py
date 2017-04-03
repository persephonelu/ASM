#coding=utf-8
import sys
import httpshandler
import json
import sql_appbk
import datetime
import logging

class CampaignsManagement:
	path = None
	httpshandler = None
	logger = None
	def __init__(self, path, httpshandler, logger):
		self.path = path
		self.httpshandler = httpshandler
		self.logger = logger

	def get_campaign_with_id(self, campaignID):
		url = path + "/" + campaignID;
		return self.httpshandler.get_response(url)

	def get_campaign_list(self):
		result = '';
		try:
			response = self.httpshandler.get_response(self.path)
			responseJson = response.read()
			if response.status != 200:
				raise Exception(json.loads(responseJson)['error'])

			result = json.loads(responseJson)['data']
		except Exception,e:
			result = str(e)
		return json.dumps(result)

	def get_adgroups_list(self, campaignId):
		result = ''
		try:
			if campaignId is not None:
				sql_com = "select id from asm_campaign where auto_id=" + campaignId
				campaigns = sql_appbk.mysql_com(sql_com)
				for campaign in campaigns:
					url = self.path + "/" + campaign['id'] + "/adgroups"
					response = self.httpshandler.get_response(url)
					responseJson = response.read()

					if response.status != 200:
						raise Exception(json.loads(responseJson)['error'])
					result = json.loads(responseJson)['data']
		except Exception,e:
			result = str(e)
		return json.dumps(result)

	def get_all_targetingKeywords_By_adgroupId(self, adgroupId):
		result = ''
		try:
			if adgroupId is not None:
				sql_com = "select * from asm_adgroup where auto_id=" + adgroupId
				adgroups = sql_appbk.mysql_com(sql_com)
				for adgroup in adgroups:
					url = self.path + "/" + adgroup['campaignId'] + "/adgroups/" + adgroup['id']
					
					response = self.httpshandler.get_response(url)
					responseJson = response.read()
					
					if response.status != 200:
						 raise Exception(json.loads(responseJson)['error'])
					result = json.loads(responseJson)['data']['keywords']
		except Exception,e:
			result = str(e);
		return json.dumps(result)	
	def get_adgroup_by_id(self, campaignID, adgroupsID):
		url = path + "/" + campaignID + "/adgroups/" + adgroupsID
		return self.httpshandler.get_response(url)

	def query_campaign(self, email, campaignId):
		status = {}
		status['status'] = 0;
		try:
			sql_com=''
			if campaignId is not None:
				sql_com = "select * from asm_campaign where localstat=0 and email='" + email + "' and auto_id=" + campaignId
			else:
				sql_com = "select * from asm_campaign where localstat=0 and email='" + email + "'"
			result = sql_appbk.mysql_com(sql_com)

			for ret in result:
				self.logger.info("Begin update a campaign for User " + email)
				sql = "select * from asm_adgroup where localstat = 0 and appbk_campaign_id=" + str(ret['auto_id'])
				adGroups = sql_appbk.mysql_com(sql)

				if ret['id'] is not None:
					#print "here"
					response = self.update_campaign(ret)
					responseJson = response.read()
					#print responseJson
					if response.status != 200:
						status['status'] = -1
						status['msg'] = response.reason
						status['error'] = json.loads(responseJson)['error']
						self.logger.error("User " + str(email) + ": update a campaign " + str(ret['auto_id']) + " Error")
						return json.dumps(status)

					campaign = json.loads(responseJson)['data']
					response = self.save_campaign(text=campaign, auto_id=ret['auto_id'])

					for adgroup in adGroups:
						if adgroup['id'] is not None:
							response = self.update_adgroup(adgroup)
							responseJson = response.read()

							if response.status != 200:
								status['status'] = -1
								status['msg'] = response.reason
								status['error'] = json.loads(responseJson)['error']
								self.logger.error("User " + str(email) + ": update a adgroup " + str(adgroup['id']) + " for a campaign " + str(ret['auto_id']) + " Error")
								return json.dumps(status)

							adgroupJson = json.loads(responseJson)['data']
							response = self.save_adgroup(adgroupJson=adgroupJson, auto_id=adgroup['auto_id'])
						else:
							response = self.create_new_adgroup(campaignId=ret['id'], adgroup=adgroup)
							responseJson = response.read();
							if response.status != 200:
								status['status'] = -1
								status['msg'] = response.reason
								status['error'] = json.loads(responseJson)['error']
								self.logger.error("User " + str(email) + ": create a adgroup for a campaign " + str(ret['auto_id']) + " Error")
								return json.dumps(status)
									#response = '{"data":{"id":10836463,"campaignId":10362102,"name":"appbk_g","cpaGoal":{"amount":"1","currency":"USD"},"storefronts":["US"],"startTime":"2016-11-06T01:00:00.000","endTime":null,"automatedKeywordsOptIn":false,"defaultCpcBid":{"amount":"0.1","currency":"USD"},"keywords":[],"negativeKeywords":[],"targetingDimensions":null,"modificationTime":"2016-11-04T05:24:30.055","status":"ENABLED","servingStatus":"NOT_RUNNING","servingStateReasons":["CAMPAIGN_NOT_RUNNING","START_DATE_IN_THE_FUTURE"],"displayStatus":"ON_HOLD"},"pagination":null,"error":null}'
							adgroupJson = json.loads(responseJson)['data']
							response = self.save_adgroup(adgroupJson=adgroupJson, auto_id=adgroup['auto_id'])
					status['msg'] = "更新广告计划成功"

				else:
					self.logger.info("Begin create a campaign for User " + email)
					response = self.create_new_campaign(ret, adGroups)
					responseJson = response.read();

					if response.status != 200:
						status['status'] = -1
						status['msg'] = response.reason
						status['error'] = json.loads(responseJson)['error']
						self.logger.error("User " + str(email) + ": create a campaign " + str(ret['auto_id']) + " Error")
						return json.dumps(status)

					campaign = json.loads(responseJson)['data']
					self.save_campaign(text=campaign, auto_id=ret['auto_id'])
					for adgroup in campaign['adGroups']:
						for item in adGroups:
							if item['name'] == adgroup['name']:
								self.save_adgroup(adgroupJson=adgroup, auto_id=item['auto_id'])
								break
					status['msg'] = "创建广告计划成功"
		except Exception,e:
			self.logger.error("User " + str(email) + ": create or update a campaign " + str(ret['auto_id']) + " failed")
		return json.dumps(status)

	def query_adgroups(self, email, adgroupId):
		status = {}
		status['status'] = 0;
		status['msg'] = "Success!"
		result = None
		try:
			if adgroupId is not None:
				#print "here"
				sql_com = "select * from asm_adgroup where auto_id=" + adgroupId
				adgroups = sql_appbk.mysql_com(sql_com);
				self.handleAdGroup(adgroups)
			else:
				sql_com = "select id, auto_id from asm_campaign where localstat=1 and displayStatus=\"running\" and email=\"" + email + "\""
				campaigns = sql_appbk.mysql_com(sql_com)			
				for campaign in campaigns:				
					sql_com = "select * from asm_adgroup where localstat=0 and appbk_campaign_id=" + str(campaign['auto_id'])
					adgroups = sql_appbk.mysql_com(sql_com)
					self.handleAdGroup(adgroups)
						
		except Exception,e:
			self.logger.error("User " + email + ": create or update adgroup failed")
			self.logger.error("Exception : " + str(e))
			status['status'] = -1
			status['msg'] = "Request Failed"
			status['error'] = str(e)
		return status

	def handleAdGroup(self, adgroups):
		for adgroup in adgroups:
			if adgroup['id'] is not None:
				response = self.update_adgroup(adgroup)
				responseJson = response.read()

				if response.status != 200:
					raise Exception(json.loads(responseJson)['error'])

				adgroupJson = json.loads(responseJson)['data']
				response = self.save_adgroup(adgroupJson=adgroupJson, auto_id=adgroup['auto_id'])
			else:
				response = self.create_new_adgroup(campaignId=adgroup['campaignId'], adgroup=adgroup)
				responseJson = response.read();
				
				if response.status != 200:
					raise Exception(json.loads(responseJson)['error'])
		
				adgroupJson = json.loads(responseJson)['data']
				response = self.save_adgroup(adgroupJson=adgroupJson, auto_id=adgroup['auto_id'])

		return 0

	def create_new_campaign(self, campaign, adGroups):
		newCampaign = {}
		newCampaign['adamId'] 	= campaign['adamId']
		newCampaign['orgId']	= campaign['orgId']
		newCampaign['name']		= campaign['name']
		budgetAmount = {}
		budgetAmount["amount"] 	= str(campaign['budgetAmount'])
		budgetAmount["currency"] = campaign['currency']

		newCampaign['budgetAmount'] = budgetAmount;
		dailyBudgetAmount = {}
		dailyBudgetAmount["amount"] 	= str(campaign['dailyBudgetAmount'])
		dailyBudgetAmount["currency"] 	= campaign['currency']
		newCampaign['dailyBudgetAmount'] = dailyBudgetAmount;
		
		if campaign['locInvoiceDetails'] is not None:
			newCampaign['locInvoiceDetails'] = campaign['locInvoiceDetails']

		if campaign['budgetOrders'] is not None:
			newCampaign['budgetOrders'] = campaign['budgetOrders']

		if campaign['status'] is not None:
			newCampaign['status'] = campaign['status']

		adGroupList = []
		for item in adGroups:
			adgroup = {}
			adgroup['name'] = item['name']
			defaultCpcBid = {};
			defaultCpcBid['amount'] = str(item['defaultCpcBid'])
			defaultCpcBid['currency'] = "USD"
			adgroup['defaultCpcBid'] = defaultCpcBid

			if item['cpaGoal'] is not None:
				cpaGoal = {}
				cpaGoal['amount'] = str(item['cpaGoal'])
				cpaGoal['currency'] = "USD"
				adgroup['cpaGoal'] = cpaGoal

			adgroup['storefronts']	= item['storefronts'].split("|")

			adgroup['startTime'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000")
			if item['startTime'] is not None:
				adgroup['startTime'] = item['startTime'].strftime("%Y-%m-%dT%H:%M:%S.000")

			if item['endTime'] is not None:
				adgroup['endTime'] = item['endTime'].strftime("%Y-%m-%dT%H:%M:%S.000")

			if item['automatedKeywordsOptIn'] is not None:
				if item['automatedKeywordsOptIn']:
					adgroup['automatedKeywordsOptIn'] = "true"
				else:
					adgroup['automatedKeywordsOptIn'] = "false"

			if item['targetedDimensions'] is not None:
				adgroup['targetedDimensions'] = item['targetedDimensions']

			if item['status'] is not None:
				adgroup['status'] = item['status']

			adGroupList.append(adgroup)

		newCampaign['adGroups']	= adGroupList

		header = {"Content-type": "application/json"}
		#print json.dumps(newCampaign)
		return self.httpshandler.do_post(self.path, json.dumps(newCampaign), header)

	def update_campaign(self, campaign):
		newCampaign = {}
		newCampaign['name']		= campaign['name']
		budgetAmount = {}
		budgetAmount["amount"] 	= str(campaign['budgetAmount'])
		budgetAmount["currency"] = campaign['currency']

		newCampaign['budgetAmount'] = budgetAmount;
		dailyBudgetAmount = {}
		dailyBudgetAmount["amount"] 	= str(campaign['dailyBudgetAmount'])
		dailyBudgetAmount["currency"] 	= campaign['currency']
		newCampaign['dailyBudgetAmount'] = dailyBudgetAmount;
		newCampaign['status']	= campaign['status']

		if campaign['locInvoiceDetails'] is not None:
			newCampaign['locInvoiceDetails'] = campaign['locInvoiceDetails']

		if campaign['budgetOrders'] is not None:
			newCampaign['budgetOrders'] = campaign['budgetOrders'].split("|")

		header = {"Content-type": "application/json"}
		#print json.dumps(newCampaign)
		url = self.path + "/" + str(campaign['id'])
		return self.httpshandler.do_put(url, json.dumps(newCampaign), header)

	def update_adgroup(self, adgroup):
		adGroupJson = {};
		adGroupJson['name'] = adgroup['name']

		defaultCpcBid = {};
		defaultCpcBid['amount'] = str(adgroup['defaultCpcBid'])
		defaultCpcBid['currency'] = "USD"
		adGroupJson['defaultCpcBid'] = defaultCpcBid

		if adgroup['cpaGoal'] is not None:
			cpaGoal = {}
			cpaGoal['amount'] = str(adgroup['cpaGoal'])
			cpaGoal['currency'] = "USD"
			adGroupJson['cpaGoal'] = cpaGoal;

		if adgroup['automatedKeywordsOptIn'] is not None:
			if adgroup['automatedKeywordsOptIn']:
				adGroupJson['automatedKeywordsOptIn'] = "true"
			else:
				adGroupJson['automatedKeywordsOptIn'] = "false"

		if adgroup['targetedDimensions'] is not None:
			adGroupJson['targetedDimensions'] = adgroup['targetedDimensions']

		if adgroup['status'] is not None:
			adGroupJson['status'] = adgroup['status']

		header = {"Content-type": "application/json"}
		#print json.dumps(adGroupJson)
		url = self.path + "/" + str(adgroup['campaignId']) + "/adgroups/" + str(adgroup['id'])
		return self.httpshandler.do_put(url, json.dumps(adGroupJson), header)

	def create_new_adgroup(self, campaignId, adgroup):
		newGroup = {}
		
		newGroup['campaignId'] = campaignId
		newGroup['name'] = adgroup['name']
		if adgroup['cpaGoal'] is not None:
			cpaGoal = {}
			cpaGoal['amount'] = str(adgroup['cpaGoal'])
			cpaGoal['currency'] = "USD"
			newGroup['cpaGoal'] = cpaGoal


		defaultCpcBid = {};
		defaultCpcBid['amount'] = str(adgroup['defaultCpcBid'])
		defaultCpcBid['currency'] = "USD"
		newGroup['defaultCpcBid'] = defaultCpcBid
		newGroup['storefronts']	= adgroup['storefronts'].split("|")

		newGroup['startTime'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000")
		if adgroup['startTime'] is not None:
			newGroup['startTime'] = adgroup['startTime'].strftime("%Y-%m-%dT%H:%M:%S.000")

		if adgroup['endTime'] is not None:
			newGroup['endTime'] = adgroup['endTime'].strftime("%Y-%m-%dT%H:%M:%S.000")

		if adgroup['automatedKeywordsOptIn'] is not None:
			if adgroup['automatedKeywordsOptIn']:
				newGroup['automatedKeywordsOptIn'] = "true"
			else:
				newGroup['automatedKeywordsOptIn'] = "false"

		if adgroup['targetedDimensions'] is not None:
			newGroup['targetedDimensions'] = adgroup['targetedDimensions']

		if adgroup['status'] is not None:
			newGroup['status'] = adgroup['status']

		header = {"Content-type": "application/json"}

		url = self.path + "/" + str(adgroup['campaignId']) + "/adgroups"
		return self.httpshandler.do_post(url, json.dumps(newGroup), header)

	def save_campaign(self, text, auto_id):
		#print text
		campaign = {}
		campaign['id'] = text['id'];
		campaign['orgId'] = text['orgId']
		campaign['name'] = str(text['name'])
		campaign['budgetAmount'] = text['budgetAmount']['amount']
		campaign['currency'] = str(text['budgetAmount']['currency'])
		campaign['dailyBudgetAmount'] = text['dailyBudgetAmount']['amount']
		campaign['adamId'] = text['adamId']

		if text['dailyBudgetAmount'] is not None:
			campaign['dailyBudgetAmount'] = text['dailyBudgetAmount']['amount']

		if text['paymentModel'] is not None:
			campaign['paymentModel'] = str(text['paymentModel'])
		'''
		if text['locInvoiceDetails'] is not None:
			campaign['locInvoiceDetails'] = "|".join(text['locInvoiceDetails'])
		'''
		campaign['status'] = text['status']
		campaign['servingStatus'] = str(text['servingStatus'])

		if text['servingStateReasons'] is not None and len(text['servingStateReasons']):
			campaign['servingStateReasons'] = str("|".join(text['servingStateReasons']))

		if text['negativeKeywords'] is not None and len(text['negativeKeywords']):
			campaign['negativeKeywords'] = str("|".join(text['negativeKeywords']))

		campaign['displayStatus'] = str(text['displayStatus'])
		modificationTime = text['modificationTime'].split("T")
		campaign['modificationTime'] = str(modificationTime[0] + " " + modificationTime[1].split(".")[0])
		campaign['localstat'] = 1
		campaign['updateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		sql_com = "update asm_campaign set "
		conditions = [];
		for item in campaign:
			conditions.append(str(item) + "=\"" + str(campaign[item]) + "\"")

		sql_com += " , ".join(conditions)
		sql_com += " where auto_id=" + str(auto_id)
		sql_appbk.mysql_com(sql_com)

		return sql_com

	def save_adgroup(self, adgroupJson, auto_id):
		adgroup = {};

		adgroup['id'] = adgroupJson['id']
		adgroup['campaignId'] = adgroupJson['campaignId']
		adgroup['name'] = adgroupJson['name']

		if adgroupJson['defaultCpcBid'] is not None:
			adgroup['defaultCpcBid'] = adgroupJson['defaultCpcBid']['amount']

		if adgroupJson['cpaGoal'] is not None:
			adgroup['cpaGoal'] = adgroupJson['cpaGoal']['amount']

		adgroup['storefronts'] = "|".join(adgroupJson['storefronts'])

		startTime = adgroupJson['startTime'].split("T")
		adgroup['startTime'] = startTime[0] + " " + startTime[1].split(".")[0]

		if adgroupJson['endTime'] is not None:
			endTime = adgroupJson['endTime'].split("T")
			adgroup['endTime'] = endTime[0] + " " + endTime[1].split(".")[0]

		if adgroupJson['automatedKeywordsOptIn'] is not None:
			if adgroupJson['automatedKeywordsOptIn']:
				adgroup['automatedKeywordsOptIn'] = 1
			else:
				adgroup['automatedKeywordsOptIn'] = 0

		modificationTime = adgroupJson['modificationTime'].split("T")
		adgroup['modificationTime'] = modificationTime[0] + " " + modificationTime[1].split(".")[0]
		adgroup['status'] = adgroupJson['status']
		adgroup['servingStatus'] = adgroupJson['servingStatus']

		if adgroupJson['servingStateReasons'] is not None and len(adgroupJson['servingStateReasons']):
			adgroup['servingStateReasons'] = "|".join(adgroupJson['servingStateReasons'])
		adgroup['displayStatus'] = adgroupJson['displayStatus']
		adgroup['updateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		adgroup['localstat'] = 1

		sql_com = "update asm_adgroup set "
		conditions = [];
		for item in adgroup:
			conditions.append(str(item) + "=\"" + str(adgroup[item]) + "\"")

		sql_com += " , ".join(conditions)
		sql_com += " where auto_id=" + str(auto_id)
		sql_appbk.mysql_com(sql_com)

		return sql_com

	def find_campaigns(self):
		return self.httpshandler.do_post()

	def find_adgroups(self):
		return self.httpshandler.do_post()

if __name__== "__main__":
	response = '{"data":{"id":10836463,"campaignId":10362102,"name":"appbk_g","cpaGoal":{"amount":"1","currency":"USD"},"storefronts":["US"],"startTime":"2016-11-06T01:00:00.000","endTime":null,"automatedKeywordsOptIn":false,"defaultCpcBid":{"amount":"0.1","currency":"USD"},"keywords":[],"negativeKeywords":[],"targetingDimensions":null,"modificationTime":"2016-11-04T05:24:30.055","status":"ENABLED","servingStatus":"NOT_RUNNING","servingStateReasons":["CAMPAIGN_NOT_RUNNING","START_DATE_IN_THE_FUTURE"],"displayStatus":"ON_HOLD"},"pagination":null,"error":null}'
	ret = save_adgroup(json.loads(response)['data'])
	print ret
