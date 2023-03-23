# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    account_debit = fields.Many2one('account.account', 'Cuenta Deudora',
                                    domain=[('deprecated', '=', False)], company_dependent=True )
    account_credit = fields.Many2one('account.account', 'Cuenta Acreedora',
                                     domain=[('deprecated', '=', False)], company_dependent=True)