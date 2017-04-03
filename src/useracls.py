#coding=utf-8
import sys
import httpshandler
import json

class UserACLs:
	path = None
	httpshandler = None
	logger = None

	def __init__(self, path, httpshandler, logger):
		self.path = path
		self.httpshandler = httpshandler
		self.logger = logger

	def getUserACLs(self, email):
		response = self.httpshandler.get_response(self.path)

		result = {}
		if response.status != 200:
			result['status'] = -1
			return result

		retJson = json.loads(response.read())['data']
		result['status'] = 0
		result['msg'] = "获取信息成功"

		data = []
		for jsontext in retJson:
			element = {};
			element["orgName"] 	= jsontext["orgName"]
			element["orgId"]	= jsontext['orgId']
			element["currency"] = jsontext['currency']
			element["roleNames"] = jsontext['roleNames']
			data.append(element)
		
		result['data'] = data
		return json.dumps(result)