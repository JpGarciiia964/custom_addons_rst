# -*- coding: utf-8 -*-
#################################################################################
# Author      : POWr (<www.powr.io>)
# Copyright(c): 2019-Present POWr Inc.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'Form Builder',
    'summary': 'Create any type of form and customize it to match your site.',
    'version': '1.0',
    'description': """POWr Plugins Form Builder.""",
    'author': 'POWr.io',
    'license': 'AGPL-3',
    'support': 'support@powr.io',
    'category': 'website',
    'website': "https://www.powr.io",
    'depends': ['base', 'website', 'odoo-powr-plugins'],
    'data': [
        'views/template.xml',
        'views/website.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
