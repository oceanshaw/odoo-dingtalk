# -*- coding: utf-8 -*-

import ConfigParser,os

class JsonDict(dict):
	def __getattr__(self, attr):
		try:
			return self[attr]
		except KeyError:
			raise AttributeError(r"'JsonDict' object has no attribute '%s'" % attr)

	def __setattr__(self, attr, value):
		self[attr] = value

class Config:
	def __init__(self):
		self.cf = ConfigParser.ConfigParser()
		self.cf.read(os.path.dirname(os.path.abspath(__file__))+'/config.ini')

	def get(self,section):
		res = JsonDict()
		for k in self.cf.options(section):
			res[k] = self.cf.get(section,k)
		return res


class APIError(StandardError):
	'''
	raise APIError if receiving json message indicating failure.
	'''
	def __init__(self, error_code, error, request):
		self.error_code = error_code
		self.error = error.encode('utf-8')
		self.request = request
		StandardError.__init__(self, error)

	def __str__(self):
		return 'APIError: %s: %s, request: %s' % (self.error_code, self.error, self.request)

