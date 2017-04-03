import sys
import httpshandler

class Reportings:
	path = None
	httpshandler = None
	def __init__(self, path, httpshandler):
		self.path = path
		self.httpshandler = httpshandler

	def get_campaigns_reports(self, path):
		return self.httpshandler.do_post()

	def get_adgroup_reports(self):
		return self.httpshandler.do_post()
	
	def get_targeted_words_reports(self):
		return self.httpshandler.do_post()

	def get_search_term_reports(self):
		return self.httpshandler.do_post()
