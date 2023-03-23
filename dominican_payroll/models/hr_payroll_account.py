# -*- coding: utf-8 -*-
# MODIFICATIONS ARE IN LINE 44, 61, 100 and 103
from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()

        for slip in self:
            # Modification --> Bellow for is the connection with the employee loan to assign some values
            payslip_day = slip.date_to.day
            for loan in slip.employee_id.loan_ids.filtered(lambda loan: loan.state == 'approved'):
                if slip.pay_vacation and slip.vacation_type == 'enjoyed' and 13 <= payslip_day <= 16:
                    loan_lines = loan.loan_line_ids.filtered(lambda loan_line: loan_line.number == loan.next_fee or loan_line.number == loan.next_fee + 1)
                    for l in loan_lines:
                        l.payslip_id = slip.id
                    loan.next_fee += 2 if loan.next_fee < loan.fee_count - 1 else 1
                else:
                    loan_line = loan.loan_line_ids.filtered(lambda loan_line: loan_line.number == loan.next_fee)
                    loan_line.payslip_id = slip.id
                    loan.next_fee += 1 if loan.next_fee < loan.fee_count else 0
                if loan.next_fee == loan.fee_count and loan.loan_line_ids.filtered(lambda l: l.number == loan.next_fee).paid:
                    loan.write({'state': 'paid'})
        return res