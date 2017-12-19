# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from dtclient import DingTalkClient
from cache import Cache
from werkzeug.utils import redirect
import logging,time,json

_logger = logging.getLogger(__name__)

class Dingtalk(http.Controller):

	@http.route('/dingtalk/home', auth='public')
	def home(self):
		corpid = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpid')
		corpsecret = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_corpsecret')
		agentid = request.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_agentid')

		if not corpid or not corpsecret:
			return redirect('/')

		dt = DingTalkClient(corpid,corpsecret)
		now = int(time.time());
		dt.get_access_token()
		ticket= dt.get_jsapi_ticket()
		noncestr = 'dingtalk'
		_logger.info(http.request.httprequest.url)
		sign = dt.sign(ticket,noncestr,now,http.request.httprequest.url)
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

			if not corpid or not corpsecret:
				return {'status':-1,'msg':'未配置企业corp id和secret'}

			dt = DingTalkClient(corpid,corpsecret)
			c = Cache.factory()
			if not c.get('access_token'):
				dt.get_access_token()

			if not request.uid:
				request.uid = odoo.SUPERUSER_ID
			try:
				user = dt.get_user_info(code)
				employee = request.env['hr.employee'].sudo().search([('dingtalk_userid', '=', user['userid'])])
				if len(employee)  > 0 and employee.resource_id.user_id:
					user = employee.resource_id.user_id
					request.session.authenticate(request.session.db, user.login, user.password_crypt)
					data = {'status':0,'msg':'登录成功'}
				else:
					data = {'status': -1, 'msg': '没有权限，请联系系统管理员设置'}
			except Exception ,e:
				_logger.exception("error : %s" % str(e))
				data = {'status': -1, 'msg': str(e)}

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
			info = dt.get_sso_userinfo(code)
			_logger.info(info)
			return json.dumps(info)
		else:
			return redirect('/')
