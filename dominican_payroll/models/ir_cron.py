# -*- coding: utf-8 -*-

from odoo import sql_db
from datetime import datetime, timedelta
from odoo import api, fields, models, _

class IrCron(models.Model):
    _inherit = 'ir.cron'

    @classmethod
    def _process_job(cls, job_cr, job, cron_cr):

        def last_day_of_month(any_day):
            # Esto nunca va a fallar
            # Se acerca al mas proximo dia al final del mes, luego suma 4 y resta la diferencia del mes siguiente
            next_month = any_day.replace(day=28) + timedelta(days=4)
            # reste el número de días 'promedio' restantes para obtener el último día del mes actual, o dicho de manera programática, el día anterior del primero del mes siguiente

            return next_month - timedelta(days=next_month.day, hours=-25)

        if job['cron_name'] == 'Envío de nóminas gradual a correos':

            if job['numbercall'] == 1:
                job['numbercall'] = 50
                date = datetime.today()
                day = date.day
                month = date.month

                if day <= 15:
                    next_date = last_day_of_month(datetime(date.year, month, day))
                    job['nextcall'] = next_date - timedelta(days=1) if next_date.day == 31 else next_date
                elif 27 < day < 31:
                    next_date = datetime(date.year + 1 if date.month == 12 else date.year, 1 if date.month == 12 else month + 1, 15)

                    job['nextcall'] = next_date

        res = super(IrCron, cls)._process_job(job_cr, job, cron_cr)
        return res
