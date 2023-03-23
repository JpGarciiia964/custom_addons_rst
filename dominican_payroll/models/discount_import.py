# -*- coding: utf-8 -*-

from odoo import fields, models


class PayrollDiscountConfig(models.Model):
    _name = 'payroll.discount.config'
    _description = "Modelo para configurar los codigos de los descuentos en la nomina de empleados"
    _sql_constraints = [('unique_input_rel', 'UNIQUE(code_rel)', 'Solo puede tener una configuración por descuento!')]
    _rec_name = 'name'

    name = fields.Char(string="Nombre", required=True)
    code_rel = fields.Many2one('hr.payslip.input.type', required=True)
    code = fields.Char(related='code_rel.code', string="Discount Code", store=True)
    active = fields.Boolean(default=True, string="Active")


class PayrollDiscountImport(models.Model):
    _name = 'payroll.discount.import'
    _description = "Modelo para cargar los descuentos de nomina a los empleados"
    _sql_constraints = [('amount_check', 'CHECK(amount > 0)', 'El monto debe ser mayor a 0!')]

    employee_id = fields.Many2one('hr.employee', string="Empleado", required=True)
    date_from = fields.Date(string="Fecha desde", required=True)
    date_to = fields.Date(string="Fecha hasta", required=True)
    discount_code = fields.Char(string="Código de descuento", required=True)
    amount = fields.Float(string="Monto", required=True)
