# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from werkzeug import url_encode

_logger = logging.getLogger(__name__)


class HrPayslipBatchwiseRegisterPaymentWizard(models.TransientModel):

    _name = "hr.payslip.batchwise.register.payment.wizard"
    _description = "Batch Wise Register Payment wizard"

    batch_id = fields.Many2one('hr.payslip.run','Batch Name')
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    amount = fields.Monetary(string='Payment Amount')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True)
    communication = fields.Char(string='Memo')
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")

    @api.one
    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        if not self.journal_id:
            self.hide_payment_method = True
            return
        journal_payment_methods = self.journal_id.outbound_payment_method_ids
        self.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            return {'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}

    @api.multi
    def expense_post_payment(self):
        self.ensure_one()
        for batch_id in self.batch_id:
            for payslip_lines in batch_id.slip_ids:
                if not payslip_lines.employee_id.address_home_id:
                    raise ValidationError(_('Please Define Employee Private Address'))

            for payslip in batch_id.slip_ids:
                if payslip.state == 'done':
                    payment_values = {
                        'partner_type': 'supplier',
                        'payment_type': 'outbound',
                        'partner_id': payslip.employee_id.address_home_id.id,
                        'journal_id': self.journal_id.id,
                        'company_id': self.company_id.id,
                        'payment_method_id': self.payment_method_id.id,
                        'amount': payslip.total_amount,
                        'currency_id': self.currency_id.id,
                        'payment_date': self.payment_date,
                        'communication': self.communication,
                        'writeoff_label': 'Payslip Payment'
                    }

                    # Create payment and post it
                    payment = self.env['account.payment'].create(payment_values)
                    payment.post()
                    # for move in payment.move_line_ids:
                    #     move.name = +
                    # Log the payment in the chatter
                    body = (_("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made.") % (payment.amount, payment.currency_id.symbol, url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, payslip.name))
                    payslip.message_post(body=body)

                    # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
                    account_move_lines_to_reconcile = self.env['account.move.line']
                    for line in payment.move_line_ids + payslip.move_id.line_ids:
                        if line.account_id.internal_type == 'payable':
                            account_move_lines_to_reconcile |= line
                    account_move_lines_to_reconcile.reconcile()
                payslip_paid_search = self.env['hr.payslip'].search([('payslip_run_id','=', batch_id.id),('state','=','paid')])
                if payslip_paid_search:
                    if len(batch_id.slip_ids) == len(payslip_paid_search):
                        self.batch_id.write({'state':'paid'})

        return {'type': 'ir.actions.act_window_close'}