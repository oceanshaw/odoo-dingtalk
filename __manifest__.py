# -*- coding: utf-8 -*-
{
    'name': "钉钉同步",

    'summary': """
        钉钉同步""",

    'description': """
        钉钉员工和部门同步
    """,

    'author': "Ocean",
    'website': "http://www.ifeige.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/hr.xml',
        'views/templates.xml',
        'views/res_config.xml',
        'views/multi_actions.xml',
        'views/actions.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable':True,
    'application':True,
    'auto_install':False,
}