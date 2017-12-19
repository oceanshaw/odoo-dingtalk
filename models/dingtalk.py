# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from dtclient import DingTalkClient
from cache import Cache

_logger = logging.getLogger(__name__)


def _get_client(obj):
	c = Cache.factory()
	if not c.has('access_token'):
		corpid = obj.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpid')
		corpsecret = obj.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpsecret')
		dt = DingTalkClient(corpid, corpsecret)
		try:
			dt.get_access_token()
		except APIError:
			raise Exception(APIError)
	else:
		dt = DingTalkClient()
	return dt

class DingTalkDepartment(models.Model):
	_inherit = "hr.department"

	dingtalk_id = fields.Integer("钉钉ID", readonly=True)
	dingtalk_create_deptgroup = fields.Boolean("是否同步创建企业群")
	dingtalk_auto_adduser = fields.Boolean("新人是否自动入群")
	dingtalk_order = fields.Integer("在父部门中的次序")
	dingtalk_dept_hiding = fields.Boolean("是否隐藏部门")


	@api.multi
	def dingtalk_get_department_detail(self):
		"""获取部门详情"""
		dt = _get_client(self)

		for record in self:
			if not record.dingtalk_id:
				pass

			department = dt.get_department_detail(record.dingtalk_id)
			_logger.info(department)
			record.dingtalk_order = department['order']
			record.dingtalk_dept_hiding = department['deptHiding']
			record.dingtalk_auto_adduser = department['autoAddUser']
			record.dingtalk_create_deptgroup = department['createDeptGroup']


	@api.multi
	def dingtalk_update_department(self):
		"""创建或者更新部门"""
		dt = _get_client(self)

		for record in self:
			if not record.parent_id or not record.parent_id.dingtalk_id:
				pass

			if record.dingtalk_id:
				param = {
					"id":record.dingtalk_id,
					"name": record.name,
					"parentid": record.parent_id.dingtalk_id,
					"deptHiding": record.dingtalk_dept_hiding
				}

				result = dt.update_department(param)

				if result.get('errcode') == 0 and result.get('errmsg') in ['ok','updated']:
					_logger.info("department updated!")

			else:
				param = {
					"name": record.name,
					"parentid": record.parent_id.dingtalk_id
				}

				result = dt.create_department(param)

				if result.get('errcode') == 0 and result.get('errmsg') in ['ok','created']:
					record.dingtalk_id = result['id']

	@api.multi
	def dingtalk_get_dept_user_list(self):
		"""获取部门成员详情， GET"""
		dt = _get_client(self)

		for record in self:
			if not record.dingtalk_id:
				pass

			result = dt.get_user_list(record.dingtalk_id)
			has_more = True
			while has_more:
				has_more = result.get('hasMore')
				userlist = result['userlist']
				for user in userlist:
					employee = self.env['hr.employee'].search([('dingtalk_userid', '=', user['userid'])])
					if len(employee) == 0:
						_createvalue = {
							"name": user['name'],
							"dingtalk_userid": user['userid'],
							"dingtalk_admin": user['isAdmin'],
							"mobile_phone":user['mobile'],
							"department_id":record.id
						}
						self.env['hr.employee'].create(_createvalue)



class DingTalkUser(models.Model):
	_inherit = 'hr.employee'

	dingtalk_userid = fields.Char("钉钉唯一标识",readonly=True)
	dingtalk_admin = fields.Boolean("管理员")
	dingtalk_boss = fields.Boolean("老板")
	dingtalk_hide = fields.Boolean("隐藏")
	dingtalk_leader = fields.Boolean("部门主管")

	@api.multi
	def dingtalk_create_employee(self):
		"""创建成员"""
		dt = _get_client(self)
		for record in self:
			if not record.dingtalk_userid and record.department_id and record.department_id.ding_id:
				param = {
					"name": record.name,
					"department": [record.department_id.dingtalk_id],
					"mobile": record.mobile_phone,
				}

				result = dt.create_user(param)
				if result.get('errcode') == 0 and result.get('errmsg') in ['ok','created']:
					record.dingtalk_userid = result['userid']


			elif record.dingtalk_userid:
				param = {
					"name": record.employee_id.name,
					"userid": record.dingtalk_userid,
				}

				result = dt.update_user(param)
				if result.get('errcode') == 0 and result.get('errmsg') in ['ok','updated']:
					_logger.info("user updated!")






