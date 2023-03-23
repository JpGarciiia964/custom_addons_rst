# -*- coding: utf-8 -*


from odoo import models, fields
from datetime import datetime
import xlsxwriter
import string
import base64


class MinistryOfLabourReportWizard(models.TransientModel):
    _name = 'ministry.of.labour.report.wizard'
    _description = u"Wizard para los reportes del Ministerio del Trabajo"

    company_id = fields.Many2one('res.company', string=u"Compañía", default=lambda self: self.env.user.company_id)
    date_from = fields.Date("Desde", required=1)
    date_to = fields.Date("Hasta", required=1)
    template = fields.Selection([('dgt2', 'DGT2'),
                                 ('dgt34', 'DGT3-DGT4'),
                                 ('dgt5', 'DGT5'),
                                 ('dgt11', 'DGT11')], string="Plantilla", required=1, help="Elija el tipo de plantilla")

    ministry_of_labour_report_xlsx_file_name = fields.Char()
    ministry_of_labour_report_xlsx_binary = fields.Binary(string="Reporte de Ministerio de Trabajo XLS")

    def generate_report(self):
        if self.template == 'dgt2':
            return self.generate_dgt2_report()

        if self.template == 'dgt34':
            return self.generate_dgt34_report()

        if self.template == 'dgt5':
            return self.generate_dgt5_report()

        if self.template == 'dgt11':
            return self.generate_dgt11_report()

    def generate_dgt2_report(self):
        this = self[0]

        records = []

        working_hours = self.env['working.hours.import'].search(
            [
                ('date_from', '>=', self.date_from),
                ('date_to', '<=', self.date_to),
                '|',
                ('extra_hours_amount', '>', 0),
                ('holiday_hours_amount', '>', 0)
            ]
        )

        # contracts = self.env['hr.contract'].search(
        #                                             ['|',
        #
        #                                             '&',
        #
        #                                                 ('state', '=', 'open'),
        #
        #                                             '&',
        #
        #                                                  ('date_start', '>=', self.date_from),
        #
        #                                                  ('date_start', '<=', self.date_to),
        #
        #                                             '&',
        #
        #                                                  ('date_end', '>=', self.date_from),
        #
        #                                             '&',
        #
        #                                                  ('date_end', '<=', self.date_to),
        #
        #                                                  ('state', '=', 'cancel')])

        contracts = []
        empl = []
        for r in working_hours:
            if r.employee_id not in empl:
                contracts.append(r)
                empl.append(r.employee_id)

        # TODO DAR FORMATO

        employee_list = []

        for index, rec in enumerate(contracts):
            if rec.employee_id not in employee_list:
                employee_list.append(rec.employee_id.id)

            # Validations: type of document
            employee_document = rec.employee_id.identification_id

            if employee_document:
                document_type = 'C'

            employee_passport = rec.employee_id.passport_id

            if employee_passport:
                document_type = 'P'

            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', rec.employee_id.id)])

            records.append([
                document_type or '',  # Tipo de documento del empleado
                rec.employee_id.identification_id or '',  # Numero del documento
                '0001',  # ID Establecimiento
                contract.wage,  # Valor de la hora
            ])

            for num in range(1, 32):
                rec_working_hours = working_hours.filtered(
                    lambda wk: wk.employee_id == rec.employee_id and wk.date_from.day == num and wk.date_to.day == num)
                if rec_working_hours:
                    hours = rec_working_hours[0]
                    if hours.extra_hours_amount > 0:
                        h = hours.extra_hours_amount
                        p = 35.00
                    elif hours.holiday_hours_amount > 0:
                        h = hours.holiday_hours_amount
                        p = 100.00
                    else:
                        h = ''
                        p = ''

                    records[index].append(h)
                    records[index].append(p)

                else:
                    records[index].append('')
                    records[index].append('')

            records[index].append('')  # TODO seccion causa de prolongacion

        file_header = [u'Tipo Doc.',
                       'Número Doc.',
                       'ID Establecimiento',
                       'Valor de la hora normal (RD$)'
                       ]

        for num in range(1, 32):
            file_header.append('Hora')
            file_header.append('%')

        file_header.append('Causa de prolongación')

        mfl_date = "{0}{1}{2}".format(self.date_to.year, self.date_to.month, self.date_to.day)

        file_path = '/tmp/REPORTE-{}-{}.xlsx'.format(self.template.upper(), mfl_date)

        workbook = xlsxwriter.Workbook(file_path,
                                       {'strings_to_numbers': True})

        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1})

        # List the alphabet
        # alphabet = ["%s%d" % (l, 1) for l in string.ascii_uppercase]

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
            'ministry_of_labour_report_xlsx_file_name': file_path.replace('/tmp/', ''),
            'ministry_of_labour_report_xlsx_binary': base64.b64encode(
                open(file_path, 'rb').read())
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ministry.of.labour.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def generate_dgt34_report(self):
        this = self[0]

        records = []

        contracts = self.env['hr.contract'].search(
                                                    ['|',

                                                    '&',

                                                        ('state', '=', 'open'),

                                                    '&',

                                                         ('date_start', '>=', self.date_from),

                                                         ('date_start', '<=', self.date_to),

                                                    '&',

                                                         ('date_end', '>=', self.date_from),

                                                    '&',

                                                         ('date_end', '<=', self.date_to),

                                                         ('state', '=', 'cancel')])
        employee_list = []

        for rec in contracts:
            if rec.employee_id not in employee_list:
                employee_list.append(rec.employee_id.id)

            # Validations
            birthday = rec.employee_id.birthday

            if birthday:
                birthday = datetime.strptime(birthday, '%Y-%m-%d')
                birthday = datetime.strftime(birthday, '%d%m%Y')

            # Validations: salario

            if rec.schedule_pay == 'hourly':
                salary = (rec.wage * 8) * 23.83

            else:
                salary = rec.wage

            # Validations: type of genre
            employee_gender = rec.employee_id.gender

            if employee_gender == '':
                pass

            elif employee_gender == 'male':
                gender = 'M'

            elif employee_gender == 'female':
                gender = 'F'

            elif employee_gender == 'other':
                gender = 'O'

            # Validations: type of document
            employee_document = rec.employee_id.identification_id

            if employee_document:
                document_type = 'C'

            employee_passport = rec.employee_id.passport_id

            if employee_passport:
                document_type = 'P'

            # Validations: type of nov
            employee_startdate = rec.date_start

            if employee_startdate:
                typenov = 'INGRESO'

            employee_date_end = rec.date_end

            if employee_date_end:
                typenov = 'SALIDA'

            records.append([
                typenov or '',  # Tipo Nov.
                document_type or '',  # Tipo de documento del empleado
                rec.employee_id.identification_id or '',  # Cedula del empleado
                rec.employee_id.names,  # Nombres del empleado
                rec.employee_id.first_lastname,  # 1re. Apellido del empleado
                rec.employee_id.second_lastname,  # 2do. Apellido del empleado
                gender or '',  # Sexo
                rec.employee_id.country_id.name or '',  # Nacionalidad del empleado
                birthday or '',  # Fecha de nacimiento
                salary or 0.0,  # Salario del empleado
                rec.date_start or '',  # Fecha de ingreso
                rec.date_end or '',  # Fecha de salida
                rec.employee_id.job_id.name or '',  # Ocupacion
                rec.employee_id.job_id.description or '',  # Descripcion de la ocupacion
                '',  # Inicio Vacaciones
                '',  # Fin Vacaciones
                '',  # ID Turno
                '',  # ID Establecimiento
                '',  # Fecha Cambio
            ])

        file_header = [u'Tipo Nov.',
                       'Tipo Doc.',
                       'Número Doc.',
                       'Nombres',
                       '1re. Apellido',
                       '2do. Apellido',
                       'Sexo',
                       'Nacionalidad',
                       'Fecha Nacimiento',
                       'Salario',
                       'Fecha Ingreso',
                       'Fecha Salida',
                       'Ocupación',
                       'Desc. Ocupación',
                       'Inicio Vacaciones',
                       'Fin Vacaciones',
                       'ID Turno',
                       'ID Establecimiento',
                       'Fecha Cambio']

        mfl_date = "{0}{1}{2}".format(self.date_to.year, self.date_to.month, self.date_to.day)

        file_path = '/tmp/REPORTE-{}-{}.xlsx'.format(self.template.upper(), mfl_date)

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
            'ministry_of_labour_report_xlsx_file_name': file_path.replace('/tmp/', ''),
            'ministry_of_labour_report_xlsx_binary': base64.b64encode(
                open(file_path, 'rb').read())
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ministry.of.labour.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def generate_dgt5_report(self):
        this = self[0]

        records = []

        contracts = self.env['hr.contract'].search(['|', '&', ('state', '=', 'open'),
                                                    '&', ('date_start', '>=', self.date_from),
                                                    ('date_start', '<=', self.date_to),
                                                    '&', ('date_end', '>=', self.date_from),
                                                    '&', ('date_end', '<=', self.date_to),
                                                    ('state', '=', 'cancel')])

        payslip = self.env['hr.payslip'].search([('date_from', '>=', self.date_from),
                                                 ('date_to', '<=', self.date_to)])

        employee_list = []
        workdays_list = []
        list(set(payslip))

        person = list(
            set(payslip.filtered(lambda p: p.contract_id.id and p.contract_id.employee_id.id).mapped('contract_id').mapped('employee_id')))

        for per in person:
            sum_workdays = 0
            filtes = payslip.filtered(lambda f: f.contract_id.employee_id.id == per.id)

            for fil in filtes:
                line_sum = sum(filtes.number_of_days for filtes in fil.worked_days_line_ids)
                sum_workdays += line_sum
            workdays_list.append(sum_workdays)

        works = 0  # Variable para iterar el arreglo workdays_list
        # donde esta la lista de numero de dias trabajos por empleados

        for rec in contracts:
            if rec.employee_id not in employee_list:
                employee_list.append(rec.employee_id.id)

            employee_document = rec.employee_id.identification_id  # Documento

            # Validations : salario

            if rec.schedule_pay == 'hourly':
                day_salary = (rec.wage * 8)
                month_salary = rec.wage * 8 * 23.83
            else:
                day_salary = rec.wage / 23.83
                month_salary = rec.wage

            # Validations: documento
            if employee_document:
                document_type = 'C'

            employee_passport = rec.employee_id.passport_id

            if employee_passport:
                document_type = 'P'

            records.append([
                document_type or '',  # Tipo de documento
                rec.employee_id.identification_id or '',  # Numero del documento
                rec.date_start or '',  # Fecha de ingreso
                rec.employee_id.job_id.name or '',  # Ocupacion
                rec.employee_id.job_id.description or '',  # Descripcion de la ocupacion
                '',  # ID Turno
                '',  # ID Establecimiento
                workdays_list[works] or '',  # Dias trabajados
                round(day_salary, 2) or 0.0,  # Salario por dia
                round(month_salary, 2) or 0.0,  # Salario mensual
            ])
            works += 1

        file_header = [u'Tipo Doc.',
                       'Número Doc.',
                       'Fecha Ingreso',
                       'Ocupación',
                       'Desc. Ocupación',
                       'ID Turno',
                       'ID Establecimiento',
                       'Dias trabajados',
                       'Salario por dia',
                       'Salario Mensual']

        mfl_date = "{0}{1}{2}".format(self.date_to.year, self.date_to.month, self.date_to.day)

        file_path = '/tmp/REPORTE-{}-{}.xlsx'.format(self.template.upper(), mfl_date)

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
            'ministry_of_labour_report_xlsx_file_name': file_path.replace('/tmp/', ''),
            'ministry_of_labour_report_xlsx_binary': base64.b64encode(
                open(file_path, 'rb').read())
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ministry.of.labour.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def generate_dgt11_report(self):
        this = self[0]

        records = []

        contracts = self.env['hr.contract'].search(
                                                    ['|',

                                                    '&',

                                                        ('state', '=', 'open'),

                                                    '&',

                                                         ('date_start', '>=', self.date_from),

                                                         ('date_start', '<=', self.date_to),

                                                    '&',

                                                         ('date_end', '>=', self.date_from),

                                                    '&',

                                                         ('date_end', '<=', self.date_to),

                                                         ('state', '=', 'cancel')])

        employee_list = []

        for rec in contracts:
            if rec.employee_id not in employee_list:
                employee_list.append(rec.employee_id.id)

            # Validations: salario
            if rec.schedule_pay == 'hourly':
                salary = (rec.wage * 8) * 23.83

            else:
                salary = rec.wage

            # Validations: documento
            employee_document = rec.employee_id.identification_id  # Documento

            if employee_document:
                document_type = 'C'

            employee_passport = rec.employee_id.passport_id

            if employee_passport:
                document_type = 'P'

            records.append([
                document_type or '',  # Tipo de documento
                rec.employee_id.identification_id or '',  # Numero del documento
                salary or 0.0,  # Salario
                rec.date_start or '',  # Fecha de ingreso
                rec.employee_id.job_id.name or '',  # Ocupacion
                rec.employee_id.job_id.description or '',  # Descripcion de la ocupacion
                '',  # ID Turno
                '',  # ID Establecimiento
            ])

        file_header = [u'Tipo Doc.',
                       'Número Doc.',
                       'Salario',
                       'Fecha Ingreso',
                       'Ocupación',
                       'Desc. Ocupación'
                       'ID Turno',
                       'ID Establecimiento']

        mfl_date = "{0}{1}{2}".format(self.date_to.year, self.date_to.month, self.date_to.day)

        file_path = '/tmp/REPORTE-{}-{}.xlsx'.format(self.template.upper(), mfl_date)

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
            'ministry_of_labour_report_xlsx_file_name': file_path.replace('/tmp/', ''),
            'ministry_of_labour_report_xlsx_binary': base64.b64encode(
                open(file_path, 'rb').read())
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ministry.of.labour.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
