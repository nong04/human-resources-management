# /payroll_attendances/__manifest__.py
{
    'name': 'Payroll Attendance',
    'version': '1.0.0',
    'summary': 'Manage employee attendances and basic payroll',
    'category': 'Human Resources/Payroll',
    'sequence': 4,
    'author': 'Do Thanh Long',
    'website': 'https://github.com/nong04/human-resources-management',
    'depends': [
        'hr_management',
        'hr_leaves',
        'mail',
    ],
    'data': [
        'security/payroll_security.xml',
        'security/ir.model.access.csv',
        'data/payroll_bonus_deduction_data.xml',

        'views/res_config_settings_views.xml',
        'views/res_currency_views.xml',
        'views/payroll_bonus_deduction_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_public_leaves_views.xml',
        'views/attendance_record_views.xml',
        'views/payroll_payroll_views.xml',
        'views/payroll_payslip_views.xml',
        'views/payroll_menus.xml',
    ],
    'demo': [
        'demo/payroll_attendance_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'payroll_attendance/static/src/js/payroll_systray.js',
            'payroll_attendance/static/src/xml/payroll_systray.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}