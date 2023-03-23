# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import xlsxwriter
import string
import base64


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    payroll_xlsx_file_name = fields.Char()
    payroll_xlsx_binary = fields.Binary(string="Archivo xls para el banco")
    is_christmas_salary = fields.Boolean(string='Nómina de doble sueldo / regalía')

    def assign_worked_hours(self):
        for payslip in self.slip_ids:
            for wdl in payslip.worked_days_line_ids:
                wdl.number_of_hours = payslip.real_worked_hours

    def generate_payroll_xlsx(self):

        if len(self.slip_ids) < 1:
            raise ValidationError(u"Debe generar alguna nómina primero.")

        records = []
        cont = 1
        for rec in self.slip_ids:
            records.append([rec.employee_id.bank_account_id.bank_id.name or '',
                            rec.employee_id.bank_account_id.acc_number or '',
                            rec.employee_id.name,
                            "'" + (rec.employee_id.identification_id or ''),
                            cont,
                            rec.line_ids.filtered(lambda line_ids: line_ids.code == 'NET').total or '',
                            self.name or '',
                            rec.employee_id.work_email or ''])
            cont += 1

        payroll_date = str(self.date_end.year) + str(self.date_end.month) + str(self.date_end.day)

        file_header = ['Banco',
                       'Número de la cuenta',
                       'Nombre del empleado',
                       'Cédula',
                       'Numero de referencia',
                       'Monto de pago',
                       'Concepto',
                       u'Correo electrónico']

        file_path = '/tmp/NOMINA{}.xlsx'.format(payroll_date)
        workbook = xlsxwriter.Workbook(file_path, {'strings_to_numbers': True})
        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1})

        # List the alphabet
        alphabet = ["%s%d" % (l, 1) for l in string.ascii_uppercase]

        for letter, header in zip(alphabet, file_header):
            worksheet.write(str(letter), str(header), bold)

        row = 1
        for rec in records:
            for col, detail in enumerate(rec):
                worksheet.write(row, col, detail)
            row += 1

        workbook.close()

        self.write({
            'payroll_xlsx_file_name': file_path.replace('/tmp/', ''),
            'payroll_xlsx_binary': base64.b64encode(open(file_path, 'rb').read())
        })

    def compute_all_payslips(self):
        if len(self.slip_ids) < 1:
            raise ValidationError(u"Debe generar alguna nómina primero.")
        # self.assign_worked_hours()
        for payslip in self.slip_ids.filtered(lambda slip: slip.state != 'done'):
            payslip.compute_sheet()

    def confirm_all_payslips(self):
        for payslip in self.slip_ids.filtered(lambda slip: slip.state != 'done'):
            payslip.action_payslip_done()

    @api.onchange('date_start')
    def onchange_date_start(self):
        if not self.date_start:
            return
        for payslip in self.slip_ids:
            payslip.date_from = self.date_start

    @api.onchange('date_end')
    def onchange_date_end(self):
        if not self.date_end:
            return
        for payslip in self.slip_ids:
            payslip.date_to = self.date_end

    def action_mail_send(self):
        for slip in self.slip_ids.filtered(lambda s: s.state == 'done'):
            slip.action_mail_send()


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    is_christmas_salary = fields.Boolean(string='Nómina de doble sueldo / regalía')

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        # Modificación
        christmas_struct = None
        b_value = False
        if self.is_christmas_salary:
            b_value = payslip_run.is_christmas_salary
            christmas_struct = self.env.ref('dominican_payroll.christmas_salary_structure')

        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
        ).filtered(lambda c: c.active)
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', employees.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        if (self.structure_id.type_id.default_struct_id == self.structure_id):
            work_entries = work_entries.filtered(lambda work_entry: work_entry.state != 'validated')
            if work_entries._check_if_error():
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Some work entries could not be validated.'),
                        'sticky': False,
                    }
                }

        default_values = Payslip.default_get(Payslip.fields_get())
        for contract in contracts:
            struct = None
            if christmas_struct:
                struct = christmas_struct.id
            else:
                struct = self.structure_id.id or contract.structure_type_id.default_struct_id.id

            values = dict(default_values, **{
                'employee_id': contract.employee_id.id,
                'credit_note': payslip_run.credit_note,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': struct,
            })
            payslip = self.env['hr.payslip'].new(values)
            payslip._onchange_employee()
            values = payslip._convert_to_write(payslip._cache)
            payslips += Payslip.create(values)
        # raise ValidationError("Oops!! Probando")
        payslips.compute_sheet()
        payslip_run.write({'is_christmas_salary': b_value})  # Modificación
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
