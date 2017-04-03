import sql_appbk
import ConfigParser
import random

class asmMember:
	memberDict = {};
	certPath   = None

	def __init__(self, certPath):
		self.certPath = certPath

	def getMemberInfo(self, email):
		if email in memberDict:
			return HTTPSHandler(memberDict[email][0], memberDict[email][1], restfulUrl)

		sql_com = "select * from asm_member where email='" + email + "'"
		result = sql_appbk.mysql_com(sql_com)

		return generateAuthentication(email, cert_file=result[0]['sshcert'], key_file=result[0]['sshkey'])

	def generateAuthentication(self, email, cert_file, key_file):
		cert_file_name = certPath + "/" + rand_str + ".pem"
		cert_output = open(cert_file_name, 'w')
		cert_output.write(cert_file)
		#必须close,否则ssl认证会出问题
		cert_output.close()

		#key字符串写入一个文件
		key_file_name = certPath + "/" + rand_str + ".key"
		key_output = open(key_file_name, 'w')
		key_output.write(key_file)
		key_output.close()

		authenticationList = [];
		authenticationList.append(cert_file_name)
		authenticationList.append(key_file_name)

		memberDict[email] = authenticationList
		return HTTPSHandler(key_file_name, cert_file_name, restfulUrl);
