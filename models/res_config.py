# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

import json
import requests
import time
import hmac
import hashlib
import urllib2
from dtclient import DingTalkClient

from odoo import api, fields, models


_logger = logging.getLogger(__name__)

class DingtalkConfiguration(models.TransientModel):
	_name = 'dingtalk.config.settings'
	_inherit = 'res.config.settings'

	corpid = fields.Char("corpid",default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpid'))
	corpsecret = fields.Char("corpsecret",default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpsecret'))
	access_token = fields.Char("access_token",default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_access_token'))
	jsapi_ticket = fields.Char("jsapi_ticket",default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_jsapi_ticket'))
	agentid = fields.Char("agentid",default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings','dingtalk_agentid'))
	noncestr = fields.Char("noncestr",default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings','dingtalk_noncestr'))
	expirein = fields.Char("expirein",default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings','dingtalk_expirein'))
	sso_secret = fields.Char("sso_secret",default=lambda self: self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_sso_secret'))

	@api.multi
	def set_corpid_defaults(self):
		return self.env['ir.values'].sudo().set_default(
			'dingtalk.config.settings', 'dingtalk_corpid', self.corpid)

	@api.multi
	def set_corpsecret_defaults(self):
		return self.env['ir.values'].sudo().set_default(
			'dingtalk.config.settings', 'dingtalk_corpsecret', self.corpsecret)

	@api.multi
	def set_sso_secret_defaults(self):
		return self.env['ir.values'].sudo().set_default(
			'dingtalk.config.settings', 'dingtalk_sso_secret', self.sso_secret)

	@api.multi
	def set_access_token_defaults(self):
		return self.env['ir.values'].sudo().set_default(
			'dingtalk.config.settings', 'dingtalk_access_token', self.access_token)

	@api.multi
	def set_agentid_defaults(self):
		return self.env['ir.values'].sudo().set_default(
			'dingtalk.config.settings', 'dingtalk_agentid', self.agentid)

	@api.multi
	def set_noncestr_defaults(self):
		return self.env['ir.values'].sudo().set_default(
			'dingtalk.config.settings', 'dingtalk_noncestr', self.noncestr)

	@api.multi
	def get_department_list(self):

		dt = DingTalkClient()
		departments = dt.get_department_list()

		depart_dic = {}
		for dep in departments:
			depart_dic[dep['id']] = dep

		for depart in departments:
			depart_sequence = [depart['id']]  # 初始化当前的部门id
			parent = depart.get('parentid')  # id=1的部门没有parentid这个key

			while parent > 1:
				parent_search = self.env['hr.department'].search([('dingtalk_id', '=', parent)])
				# 如果已经存在上级
				if len(parent_search) == 1:
					break
				elif len(parent_search) == 0:
					# 该上级需要创建，所以将id加进去
					depart_sequence.append(parent)
					# 新的parent
					parent = depart_dic[parent]['parentid']

			# 对要创建的部门排序
			depart_sequence.sort()

			for ds in depart_sequence:
				ds = depart_dic[ds]

				_parentid = ds.get('parentid')

				if _parentid:
					_parent = self.env['hr.department'].search([('dingtalk_id', '=', _parentid)])

				_current = self.env['hr.department'].search([('name', '=', ds['name'])])

				if len(_current) < 1:
					_create_value = {
						"name": ds['name'],
						"dingtalk_id": ds['id']
					}
					if _parentid:
						_create_value['parent_id'] = _parent.id

					self.env['hr.department'].create(_create_value)
				elif len(_current) == 1:
					_current.dingtalk_id = ds['id']
					if _parentid:
						_current.parent_id = _parent.id




