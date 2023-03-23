# -*- coding: utf-8 -*-
{
    'name': "Nómina Dominicana",

    'summary': """This module adapts Odoo Payroll and HHRR modules to the dominican standard""",

    'description': """
        
    """,

    'author': "Jose Romero, Wander Paniagua",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization/Payroll',
    'version': '14.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'hr',
                'hr_payroll',
                'hr_payroll_account',
                'contacts',
                'account'],

    # always loaded
    'data': [
        'data/res_partner.xml',
        'data/contribution_registers.xml',
        'data/salary_structure.xml',
        'data/salary_rules_categories.xml',
        'data/salary_rule_inputs.xml',
        'data/salary_rules.xml',
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        'views/hr_payslip_view.xml',
        'views/hr_payroll_structure.xml',
        'views/hr_payslip_run_view.xml',
        'views/hr_employee_loan_views.xml',
        'views/hr_employee_views.xml',
        'views/payslip_report_templates.xml',
        'views/mail_template.xml',
        'views/discount_import_views.xml',
        'views/working_hours_import_views.xml',
        'wizard/payslip_report_wizard_view.xml',
        'wizard/ministry_of_labour_report_wizard_view.xml',
    ],
    'external_dependencies': {
      'python': ['xlsxwriter', 'numpy', 'dateutil', 'numpy-financial']
    },
}