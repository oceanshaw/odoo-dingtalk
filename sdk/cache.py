# -*- coding: utf-8 -*-
import json, time, os, pickle, datetime
from util import Config


class Cache:
	@staticmethod
	def factory(adapter='file'):
		caches = {
			'file': FileCache(),
			'redis': RedisCache(),
		}
		return caches[adapter]


class CacheBase:
	def add(self, key, value, lifespan=None):
		pass

	def get(self, key):
		pass

	def has(self, key):
		pass

	def delete(self, key):
		pass

	def reset(self):
		pass


class FileCache(CacheBase):
	def __init__(self):
		cf = Config()
		self.file_name = os.path.dirname(os.path.abspath(__file__)) +'/'+ cf.get('file').folder + "/cache.txt"

	def get(self, key):
		dict_obj = self.__get_file_content()

		row = dict_obj.get(key)

		if not self.has(key):
			return None

		if self.__is_expired_row(row):
			self.delete(key)
			return None

		return row['value']

	def has(self, key):
		dict_obj = self.__get_file_content()

		if key in dict_obj:
			# check expiration before returning true
			row = dict_obj.get(key)

			if self.__is_expired_row(row):
				self.delete(key)
				return False
			return True

		return False

	def delete(self, key):
		dict_obj = self.__get_file_content()

		dict_obj.pop(key)

		self.__put_file_content(dict_obj)
		pass

	def update(self, key, value, lifespan=3600):
		dict_obj = self.__get_file_content()

		dict_obj['key'] = {
			'value': value,
			'_created_at': datetime.datetime.now(),
			'_lifetime': lifespan
		}

		self.__put_file_content(dict_obj)

	def add(self, key, value, lifespan=3600):
		dict_obj = self.__get_file_content()

		if dict_obj.get(key) is None:
			dict_obj[key] = {
				'value': value,
				'_created_at': datetime.datetime.now(),
				'_lifetime': lifespan
			}

		self.__put_file_content(dict_obj)

	def reset(self):
		dict_obj = {}
		self.__put_file_content(dict_obj)

	# private methods
	def __get_file_content(self):
		try:
			f = open(self.file_name, 'r')

			return pickle.load(f)
		except IOError:
			print("unable to open file")
			return None

	def __put_file_content(self, new_content):
		try:
			f = open(self.file_name, 'w')

			pickle.dump(new_content, f)

		except IOError:
			print("unable to write to file")
			return None

	def __is_expired_row(self, row):
		# check expiration date and if passed
		_created_at = row['_created_at']
		# total amount of seconds for the existence of the store value
		_lifetime = row['_lifetime']

		diff = datetime.datetime.now() - _created_at

		in_seconds = diff.total_seconds()

		if in_seconds > _lifetime:
			return True

		return False

class RedisCache(CacheBase):
	def __init__(self):
		pass

