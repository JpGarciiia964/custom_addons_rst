# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################
import re
import uuid
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

emails_split = re.compile(r"[;,\n\r]+")
email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")


class SurveyMailComposeMessage(models.TransientModel):
    _inherit = 'survey.mail.compose.message'

    public = fields.Selection([('email_private',
                                'Send private invitation to your audience (only one response per recipient and per invitation).'), ('public_link', 'Share the public web link to your audience.'), ('email_public_link', 'Send by email the public web link to your audience.')
                               ], string='Share options',
                              default='email_private', required=True)
    send_to = fields.Selection([('specific', 'Send to specific audience')],
                               string='Send To', default='specific', required=True)
