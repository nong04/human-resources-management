# /hr_management/__manifest__.py
{
    'name': 'HR Management',
    'version': '1.0.0',
    'summary': 'A module for managing employees, departments, and job positions.',
    'category': 'Human Resources/Employees',
    'sequence': 1,
    'author': 'Do Thanh Long',
    'website': 'https://github.com/nong04/human-resources-management',
    'depends': [
        'base',
        'mail',
        'resource',
    ],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',

        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
        'views/hr_job_views.xml',
        'views/hr_access_request_views.xml',

        'views/res_users_views.xml',
        'views/res_config_settings_views.xml',

        'views/hr_menus.xml',
    ],
    'demo': [
        'demo/hr_management_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_management/static/src/user_menu/my_profile.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}