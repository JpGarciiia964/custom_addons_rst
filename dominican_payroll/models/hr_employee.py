# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    income_type = fields.Selection([('1', 'Normal'),
                                    ('2', 'Trabajador ocasional (no fijo)'),
                                    ('3', 'Asalariado por hora o labora tiempo parcial'),
                                    ('4', 'No laboró mes completo por razones varias'),
                                    ('5', 'Salario prorrateado semanal/bisemanal'),
                                    ('6', 'Pensionado antes de la Ley 87-01'),
                                    ('7', 'Exento por Ley de pago al SDSS'),
                                    ], string='Tipo de remuneración')
    loan_ids = fields.One2many(comodel_name='hr.employee.loan', inverse_name='employee_id',
                               string=u"Préstamos")
    names = fields.Char(string="Nombres")
    employee_code = fields.Char(string="Código")
    first_lastname = fields.Char(string="1er. Apellido")
    second_lastname = fields.Char(string="2do. Apellido")

    def get_approved_loans(self):
        return self.loan_ids.filtered(lambda loan: loan.state == 'approved')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        recs = self.search([
            '|',
            ('name', operator, name),
            ('employee_code', operator, name),
        ], limit=limit)
        res = recs.name_get()
        return res

    @api.model
    def convert_to_date(self, dstr):
        return fields.date.fromisoformat(dstr)
