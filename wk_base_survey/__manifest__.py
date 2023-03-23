# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
#################################################################################
{
  "name"                 :  "Webkul Base Survey",
  "summary"              :  "Webkul Base Survey facilitates you to take the survey of the people about any particular event using a question or series of questions.",
  "category"             :  "Marketing",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/Odoo.html",
  "description"          :  """Webkul Base Survey
Base Survey
Odoo Base Survey
Survey Research
Survey Methods
Survey
Survey Maker
Online Base Survey
Online Survey
Questions to know about people
""",
  "depends"              :  ['survey'],
  "data"                 :  ['wizard/survey_mail_compose_view.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "pre_init_hook"        :  "pre_init_check",
}