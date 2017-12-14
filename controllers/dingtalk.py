# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from dtclient import DingTalkClient
from werkzeug.utils import redirect
import logging,time,json

_logger = logging.getLogger(__name__)

class Dingtalk(http.Controller):

	@http.route('/dingtalk/home', auth='public')
	def home(self):
		corpid = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpid')
		corpsecret = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpsecret')
		agentid = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_agentid')
		noncestr = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_noncestr')
		expirein = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_expirein')
		access_token = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_access_token')

		if not corpid or not corpsecret:
			return redirect('/')

		dt = DingTalkClient(corpid,corpsecret)
		now = int(time.time());
		if (now >= expirein):
			access_token = dt.get_access_token()
			request.env['ir.values'].sudo().set_default('dingtalk.config.settings', 'dingtalk_access_token',access_token)
			request.env['ir.values'].sudo().set_default('dingtalk.config.settings', 'dingtalk_expirein',now+7000)
		else:
			dt.access_token = access_token
		ticket= dt.get_jsapi_ticket()
		url = 'http://erp.ifeige.cn/dingtalk/home'
		sign = dt.sign(ticket,noncestr,now,url)
		_logger.info(ticket)
		config = {
			'nonceStr': noncestr,
			'agentId' : agentid,
			'timeStamp':now,
			'corpId':corpid,
			'signature'  :sign
		}
		_logger.info(config)

		return http.request.render('dingtalk.home',config)

	@http.route('/dingtalk/getuserinfo', auth='public')
	def userinfo(self, **kw):
		code = kw.get('code');
		if code:
			corpid = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpid')
			corpsecret = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpsecret')
			access_token = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_access_token')
			expirein = request.env['ir.values'].sudo().get_default('dingtalk.config.settings',
																	  'dingtalk_expirein')
			if not corpid or not corpsecret:
				return {'status':-1,'msg':'未配置企业corp id和secret'}
			dt = DingTalkClient(corpid,corpsecret)
			now = int(time.time());
			if (now >= expirein):
				access_token = dt.get_access_token()
				request.env['ir.values'].sudo().set_default('dingtalk.config.settings', 'dingtalk_access_token',
															accessToken)
				request.env['ir.values'].sudo().set_default('dingtalk.config.settings', 'dingtalk_expirein', now+7000)
			else:
				dt.access_token = access_token
			user = dt.get_user_info(code)
			_logger.info(user)
			data =  {
				'status':0,
				'msg':'ok',
				'data':user
			}
			_logger.info(data)
			return json.dumps(data)
		else:
			return redirect('/')

	'''
	钉钉管理员管理页面进入
	'''
	@http.route('/dingtalk/admin', auth='public')
	def admin(self, **kw):
		code = kw.get('code');
		if code:
			corpid = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpid')
			sso_secret = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_sso_secret')

			if not corpid or not sso_secret:
				return redirect('/')

			dt = DingTalkClient(corpid,sso_secret)
			dt.get_sso_token()
			info = dt.get_sso_userinfo(code)
			_logger.info(info)
			return json.dumps(info)
		else:
			return redirect('/')
