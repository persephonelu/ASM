#!/usr/bin/env python
#coding=utf-8
import httplib
import json

class HTTPSHandler:
	conn = None
	def __init__(self, key_file=None, cert_file=None, url=None):
		self.key_file = key_file
		self.cert_file = cert_file
		self.url = url
		self.do_connection()

	def __del__(self):
		if self.conn is not None:
			self.conn.close()

	def do_connection(self):
		if self.cert_file is not None and self.key_file is not None:
			self.conn = httplib.HTTPSConnection(self.url, cert_file=self.cert_file, key_file=self.key_file)
		else:
			print "cert_file is NULL"

	def do_request(self, path):
		self.conn.request('GET', path)

	def get_response(self, path):
		self.do_request(path)
		return self.conn.getresponse()

	def do_post(self, path, postfile=None, header=None):
		self.conn.request('POST', path, postfile, header)
		return self.conn.getresponse()

	def do_put(self, path, postfile, header):
		self.conn.request('PUT', path, postfile, header)
		return self.conn.getresponse()

