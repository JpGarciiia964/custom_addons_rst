# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def compute_tax_amount(self):
        amount = 0.0
        for payment in self:
            # for line in payment.line_ids.filtered(lambda l: l.move_id.is_invoice()):
            #     amount += line.move_id.amount_tax
            for inv in payment.reconciled_invoice_ids:
                amount += inv.amount_tax
            payment.amount_tax = amount
            # payment.amount_tax = amount

    amount_tax = fields.Float(compute=compute_tax_amount)
    commissioned = fields.Boolean()
    user_id = fields.Many2one('res.users', string="Vendedor", related='reconciled_invoice_ids.user_id')





