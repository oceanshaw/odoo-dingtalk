# -*- coding: utf-8 -*-

import json,requests,time,os,sys,logging,datetime
from util import Config,APIError
from cache import Cache

_logger = logging.getLogger(__name__)


'''
http call
'''
def _http_call(url, params, method='GET'):
	_logger.info('+++++++++++++++++++++++++++++')
	_logger.info('request : ' + url)
	_logger.info(params)

	if method == 'GET':
		res = requests.get(url, params=params)
	else:
		res = requests.post(url,data=params)

	if res.status_code == 200:
		data = res.json()
		_logger.info('response : ')
		_logger.info(data)

		if data['errcode'] == 0 and data['errmsg'] == 'ok':
			return data
		else:
			raise APIError(data['errcode'],data['errmsg'],url)
	else:
		raise APIError(res.status_code,'api error',url)

def _http_get(url, params):
	return _http_call(url,params)

def _http_post(url, access_token, params):
	uri = '%s?access_token=%s'%(url,access_token)
	return _http_call(uri,json.dumps(params),'POST')


class DingTalkClient:
	def __init__(self, corpid=None, corpsecret=None):
		self.corp_params = {
			'corpid': corpid,
			'corpsecret': corpsecret
		}

		cf = Config()
		self.api = cf.get('api')
		self.method = cf.get('method')
		self.cache = Cache.factory(cf.get('cache').adapter)
		self.access_token = self.cache.get('access_token')

	def get_access_token(self):
		token = self.cache.get('access_token')
		if token:
			self.access_token = token
		else:
			resp = _http_call(self.api.url_access_token, self.corp_params)
			self.access_token = resp['access_token']
			self.cache.add('access_token',self.access_token,7000)
		return self.access_token


	'''
	通过CODE换取微应用管理员的身份信息
	'''
	def get_sso_userinfo(self, code):
		token = self.cache.get('sso_token');
		if not token:
			resp = _http_call(self.api.url_sso_token, self.corp_params)
			token = resp['access_token']
			self.cache.add('sso_token', token, 7000)
		params = {'access_token': token, 'code': code}

		return _http_call(self.api.url_sso_user_info, params)

	def get_user_info(self, code):
		params = {'access_token': self.access_token, 'code':code}

		return _http_call(self.api.url_user_info, params)

	def get_jsapi_ticket(self):
		ticket = self.cache.get('jsapi_ticket');
		if not ticket:
			params = {'access_token': self.access_token}
			resp = _http_call(self.api.url_jsapi_ticket, params)
			ticket = resp['ticket']
		return ticket

	def sign(self, ticket, nonce_str, time_stamp, url):
		import hashlib
		plain = 'jsapi_ticket={0}&noncestr={1}&timestamp={2}&url={3}'.format(ticket, nonce_str, time_stamp, url)
		return  hashlib.sha1(plain).hexdigest()

	def get_user_simple_list(self, department_id, params={}):
		params.update({'access_token': self.access_token, 'department_id': department_id})
		return _http_call(self.api.url_user_list_simple, params)

	def get_user_list(self, department_id, params={}):
		params.update({'access_token': self.access_token, 'department_id': department_id})
		return _http_call(self.api.url_user_list, params)

	def create_user(self, params):
		return _http_post(self.api.url_user_create, self.access_token, params)

	def update_user(self, params):
		return _http_post(self.api.url_user_update, self.access_token, params)

	def get_department_detail(self, department_id):
		params = {'access_token': self.access_token, 'id': department_id}
		return _http_call(self.api.url_department_detail, params)

	def get_department_list(self, id=None):
		params={'access_token': self.access_token}
		if id:
			params.update({'id': id})
		data = _http_call(self.api.url_department_list, params )
		return data['department']

	def update_department(self, params):
		return _http_post(self.api.url_department_update, self.access_token, params)

	def create_department(self, params):
		return _http_post(self.api.url_department_create,self.access_token, params)

	def list_label_groups(self, size=20, offset=0):
		return self.request_list('dingtalk.corp.ext.listlabelgroups',size, offset)


	def get_corp_ext_list(self, size=20, offset=0):
		"""
		获取外部联系人
		"""
		return self.request_list('dingtalk.corp.ext.list', size, offset)

	def get_all_ext_list(self):
		"""
		获取全部的外部联系人
		"""
		size = 100
		offset = 0
		dd_customer_list = []
		while True:
			dd_customers = self.get_corp_ext_list(size=size, offset=offset)
			if len(dd_customers) <= 0:
				break
			else:
				dd_customer_list.extend(dd_customers)
				offset += size
		return dd_customer_list

	def add_corp_ext(self, contact):
		"""
		添加外部联系人
		"""
		url = self.get_request_url('dingtalk.corp.ext.add', self.access_token)
		contact = json.dumps(contact)
		resp = _http_call(url, {'contact': contact.encode('utf-8')},'POST')
		return resp

	def create_bpms_instance(self, process_code, originator_user_id, dept_id, approvers, form_component_values, agent_id=None):
		"""
		发起审批实例
		"""
		agent_id = agent_id or self.agent_id
		url = get_request_url('dingtalk.smartwork.bpms.processinstance.create', self.access_token)
		params = {}
		args = locals()
		for key in ('process_code', 'originator_user_id', 'dept_id', 'approvers', 'form_component_values',
					'agent_id', 'cc_list', 'cc_position'):
			if args.get(key, no_value) is not None:
				params.update({key: args[key]})

		return _http_call(url,params,'POST');

	def get_bpms_instance_list(self, process_code, start_time, end_time=None, size=10, cursor=0):
		"""
		企业可以根据审批流的唯一标识，分页获取该审批流对应的审批实例。只能取到权限范围内的相关部门的审批实例
		"""
		start_time = datetime.timestamp(start_time)
		start_time = int(round(start_time * 1000))
		if end_time:
			end_time = datetime.timestamp(end_time)
			end_time = int(round(end_time * 1000))
		args = locals()
		url = get_request_url('dingtalk.smartwork.bpms.processinstance.list', self.access_token)
		params = {}
		for key in ('process_code', 'start_time', 'end_time', 'size', 'cursor'):
			if args.get(key, no_value) is not None:
				params.update({key: args[key]})

		return _http_call(url,params)

	def request_list(self, method, size=20, offset=0):
		'''
		根据method获取列表
		'''
		url = self.get_request_url(method)
		params = {'size': size, 'offset': offset}
		resp = _http_call(url, params)
		data = json.loads(resp[self.method[method]]['result'])
		return data

	def get_request_url(self, method, format_='json', v='2.0', simplify='false', partner_id=None):
		"""
		根据code获取请求地址
		"""
		timestamp = self.get_timestamp()
		url = '{0}?method={1}&session={2}&timestamp={3}&format={4}&v={5}'.format(
			_config['URL_METHODS_URL'], method, self.access_token, timestamp, format_, v)
		if format_ == 'json':
			url = '{0}&simplify={1}'.format(url, simplify)
		if partner_id:
			url = '{0}&partner_id={1}'.format(url, partner_id)
		return url

	def get_timestamp(self):
		"""
		生成时间戳
		"""
		return datetime.now().strftime('yyyy-MM-dd HH:mm:ss')