# -*- coding: utf-8 -*-


from odoo import models, fields
from datetime import datetime
import xlsxwriter
import string
import base64

INCOME_TYPE = {
    '1': 'Normal',
    '2': 'Trabajador ocasional (no fijo)',
    '3': 'Asalariado por hora o labora tiempo parcial',
    '4': 'No laboró mes completo por razones varias',
    '5': 'Salario prorrateado semanal/bisemanal',
    '6': 'Pensionado antes de la Ley 87-01',
    '7': 'Exento por Ley de pago al SDSS',
}


class PayslipReportWizard(models.TransientModel):
    _name = 'payslip.report.wizard'
    _description = u"Wizard para los reportes de nómina"

    company_id = fields.Many2one('res.company', string=u"Compañía", default=lambda self: self.env.user.company_id)
    date_from = fields.Date("Desde", required=1)
    date_to = fields.Date("Hasta", required=1)
    type = fields.Selection([('one', 'Individual'),
                             ('department', 'Departamento'),
                             ('by_batch', 'Procesamiento'),
                             ('global', 'Global'), ('tss_news', 'Novedades TSS')],
                            string="Tipo", default='by_batch', required=1,
                            help="Elija el tipo de reporte")
    employee_id = fields.Many2one('hr.employee', string='Empleado')
    department_id = fields.Many2one('hr.department', string='Departamento')
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Procesamiento')
    payslip_report_xlsx_file_name = fields.Char()
    payslip_report_xlsx_binary = fields.Binary(string="Reporte de nómina XLS")
    tss_xlsx_file_name = fields.Char()
    tss_xlsx_file_binary = fields.Binary(string="Archivo xls para TSS")

    def get_name(self, report_type):
        names = {
            'one': self.employee_id.name if self.employee_id else '',
            'department': self.department_id.name if self.department_id else '',
            'by_batch': self.payslip_run_id.name if self.payslip_run_id else '',
            'global': ''
        }

        if report_type != 'global':
            name = " " + str(names.get(report_type)).upper() + " "
        else:
            name = " "

        return name

    def generate_report(self):
        if self.type == 'tss_news':
            return self.generate_tss_report()
        this = self[0]
        company_id = self.company_id.id
        date_from = self.date_from
        date_to = self.date_to
        report_type = self.type
        domain = [('date_from', '>=', date_from), ('date_to', '<=', date_to), ('company_id', '=', company_id)]
        if report_type == 'by_batch':
            payslips = self.payslip_run_id.slip_ids
        else:
            domain.append(('state', 'in', ['draft', 'verify', 'done']))
            if report_type == 'one':
                employee_id = self.employee_id.id
                domain.append(('employee_id', '=', employee_id))

            elif report_type == 'department':
                department_id = self.department_id.id
                domain.append(('employee_id.department_id', '=', department_id))

            payslips = self.env['hr.payslip'].search(domain, order='employee_id').sorted('date_to')

        employee_list = []
        for rec in payslips:
            if rec.employee_id.id not in employee_list:
                employee_list.append(rec.employee_id.id)

        file_header = ['Fecha',
                       'Empleado',
                       'Salario Mensual',
                       'Salario Quincenal',
                       'Horas Extras',
                       'Incentivos',
                       'Vacaciones',
                       'Comisiones',
                       'Financiera',
                       'Otros descuentos',
                       'Avances',
                       u'Seguro Complementario',
                       u'Retención AFP',
                       u'Retención SFS',
                       u'Retención ISR',
                       'Saldo a Favor ISR',
                       'Salario Cotizable ISR',
                       'Salario Cotizable TSS/INFOTEP',
                       u'Contribución AFP',
                       u'Contribución SFS',
                       u'Contribución SRL',
                       u'Contribución INFOTEP',
                       u'Cafetería',
                       u'Farmacia',
                       u'Ahorro',
                       u'Restaurante',
                       'Salario a pagar']
        records = []
        for i in employee_list:

            for rec in payslips.filtered(lambda payslip: payslip.employee_id.id == i):
                records.append([rec.date_to,
                                rec.employee_id.name,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'BASIC').total * 2 or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'BASIC').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'HOREX').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'INCENT').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'VACA').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'COMM').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'FINAN').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'OTDESC').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'AVAN').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'SEGMED').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'SVDS').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'SFST').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'ISR').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'SFISR').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'SCISR').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'GROSS').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'SVDS E').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'SFS E').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'SRL E').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'CINF').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'CAFE').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'FARMA').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'AHORRO').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'REST').total or 0.0,
                                rec.line_ids.filtered(lambda line_ids: line_ids.code == 'NET').total or 0.0])

        file_path = '/tmp/REPORTE NOMINA{}de {} a {}.xlsx'.format(self.get_name(report_type), date_to, date_from)
        workbook = xlsxwriter.Workbook(file_path, {'strings_to_numbers': True})
        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1})

        # List the alphabet
        # alphabet = ["%s%d" % (l, 1) for l in string.ascii_uppercase]
        #
        # for letter, header in zip(alphabet, file_header):
        #     worksheet.write(str(letter), str(header), bold)
        for col_num, data in enumerate(file_header):
            worksheet.write(0, col_num, data, bold)

        row = 1
        for rec in records:
            for col, detail in enumerate(rec):
                worksheet.write(row, col, detail)
            row += 1

        workbook.close()

        this.write({
            'payslip_report_xlsx_file_name': file_path.replace('/tmp/', ''),
            'payslip_report_xlsx_binary': base64.b64encode(open(file_path, 'rb').read())
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payslip.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def generate_tss_report(self):
        this = self[0]
        ###############Resumen novedades TSS#####################

        records = []

        payslips = self.env['hr.payslip'].search([('date_from', '>=', self.date_from),
                                                  ('date_to', '<=', self.date_to),
                                                  ('state', 'in', ['draft', 'verify', 'done']),
                                                  ('company_id', '=', self.company_id.id)])
        employee_list = []
        for rec in payslips:
            if rec.employee_id not in employee_list:
                employee_list.append(rec.employee_id)

        for employee in employee_list:
            gross = 0

            for line in payslips.filtered(lambda p: p.employee_id.id == employee.id).mapped('line_ids').filtered(lambda l: l.code == 'GROSS'):
                day = line.slip_id.date_to.day
                if 25 <= day <= 31:
                    gross = line.total
                else:
                    gross = line.total - (employee.contract_id.wage / 2)
            horex = sum(line.total for line in payslips.filtered(lambda p: p.employee_id.id == employee.id).mapped('line_ids').filtered(lambda l: l.code in ['HOREX', 'HEPQ']))
            APORA = sum(line.total for line in payslips.filtered(lambda p: p.employee_id.id == employee.id).mapped('line_ids').filtered(lambda l: l.code in ['APORAFP', 'APORSFS']))

            birthday = employee.birthday
            if birthday:
                # birthday = datetime.strptime(birthday, '%Y-%m-%d')
                birthday = datetime(year=birthday.year, month=birthday.month, day=birthday.day)
                birthday = datetime.strftime(birthday, '%d%m%Y')

            employee_document = ''
            document_type = ''
            if employee.passport_id:
                employee_document = employee.passport_id
                document_type = 'P'
            else:
                employee_document = employee.identification_id
                document_type = 'C'

            records.append([
                 document_type or '',
                 employee_document or '',  # Documento del empleado
                 employee.names or '',  # Nombres del empleado
                 employee.first_lastname or '',  # 1er apellido
                 employee.second_lastname or '',  # 2do apellido
                 employee.gender or '',  # Sexo
                 birthday or '',  # Fecha de nacimiento
                 gross,  # Total de ingresos sin horas extras
                 APORA or 0.0,  # Aportes adicionales
                 horex,  # Horas extras = (HOREX + HEPQ)
                 INCOME_TYPE.get(employee.income_type),
                 gross + horex # Totales = (Total de ingreso + HOREX + HEPQ)
            ])

        payroll_date = "{0}{1}{2}".format(self.date_to.year, self.date_to.month, self.date_to.day)

        file_header = ['Tipo de documento',
                       'Documento',
                       'Nombres',
                       '1er apellido',
                       '2do apellido',
                       'Sexo',
                       'Fecha de nacimiento',
                       u'Salario Cotizable',
                       'Aportes Adicionales',
                       'Otras Remuneraciones',
                       'Tipo ingreso',
                       'Totales']


        file_path = '/tmp/RESUMEN-TSS-{}.xlsx'.format(payroll_date)
        workbook = xlsxwriter.Workbook(file_path,
                                       {'strings_to_numbers': True})
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

        this.write({
            'tss_xlsx_file_name': file_path.replace('/tmp/', ''),
            'tss_xlsx_file_binary': base64.b64encode(
                open(file_path, 'rb').read())
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payslip.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
