# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    rules_generated = fields.Boolean(string="Generadas Reglas", compute='_check_count')

    @api.depends('rule_ids')
    def _check_count(self):
        for rec in self:
            if len(rec.rule_ids) > 0:
                rec.rules_generated = True
            else:
                rec.rules_generated = False

    @api.model
    def default_get(self, fields_list):
        res = super(PayrollStructure, self).default_get(fields_list)
        res['rule_ids'] = []
        return res

    def fill_rule_structure(self):

        struct_f_id = self.env.ref('dominican_payroll.structure_permanent_employees').id
        struct_c_id = self.env.ref('dominican_payroll.christmas_salary_structure').id
        struct_ex_id = self.env.ref('dominican_payroll.structure_foreign_employees').id
        employee_rules = self.env['hr.salary.rule'].search([('struct_id', '=', struct_f_id)])
        double_rules = self.env['hr.salary.rule'].search([('struct_id', '=', struct_c_id)])
        foreign_rules = self.env['hr.salary.rule'].search([('struct_id', '=', struct_ex_id)])

        rules = []

        if employee_rules and self.country_id.code == 'DO' and self.schedule_pay == 'bi-weekly':
            for rule in employee_rules:
                rules.append((0, 0, {
                    'name': rule.name,
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'category_id': rule.category_id.id,
                    'condition_select': rule.condition_select,
                    'condition_python': rule.condition_python,
                    'amount_select': rule.amount_select,
                    'amount_python_compute': rule.amount_python_compute,
                }))
        elif double_rules and self.schedule_pay == 'annually':
            for rule in double_rules:
                rules.append((0, 0, {
                    'name': rule.name,
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'category_id': rule.category_id.id,
                    'condition_select': rule.condition_select,
                    'condition_python': rule.condition_python,
                    'amount_select': rule.amount_select,
                    'amount_python_compute': rule.amount_python_compute,
                }))

        elif foreign_rules and not self.country_id and self.schedule_pay == 'bi-weekly':
            for rule in foreign_rules:
                rules.append((0, 0, {
                    'name': rule.name,
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'category_id': rule.category_id.id,
                    'condition_select': rule.condition_select,
                    'condition_python': rule.condition_python,
                    'amount_select': rule.amount_select,
                    'amount_python_compute': rule.amount_python_compute,
                }))

        self.rule_ids = rules
