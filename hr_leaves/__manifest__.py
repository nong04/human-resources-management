# /hr_leaves/__manifest__.py
{
    'name': 'Leave Management',
    'version': '1.0.0',
    'summary': 'Manage leave requests and allocations, integrated with HR Management.',
    'category': 'Human Resources/Leaves',
    'sequence': 3,
    'author': 'Do Thanh Long',
    'website': 'https://github.com/nong04/human-resources-management',
    'depends': [
        'hr_management',
        'mail',
    ],
    'data': [
        'security/hr_leaves_security.xml',
        'security/ir.model.access.csv',
        'data/hr_leaves_data.xml',

        'views/hr_leaves_type_views.xml',
        'views/hr_public_leaves_views.xml',
        'views/hr_leaves_request_views.xml',
        'views/hr_leaves_allocation_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_leaves_calendar_views.xml',

        'views/hr_leaves_menus.xml',
    ],
    'demo': [
        'demo/hr_leaves_demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
