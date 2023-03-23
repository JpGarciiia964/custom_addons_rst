# -*- coding: utf-8 -*-
#################################################################################
# Author      : POWr (<www.powr.io>)
# Copyright(c): 2012-Present POWr Inc.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'POWr Plugins',
    'summary': 'Creates a POWr Plugins section inside the Odoo Website Editor to easily add POWr Plugins to your site!',
    'version': '1.0',
    'description': """POWr Plugins.""",
    'author': 'POWr.io',
    'license': 'AGPL-3',
    'category': 'website',
    'website': "https://www.powr.io",
    'depends': ['base', 'website'],
    'data': [
        'views/website.xml',
        'views/template.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
