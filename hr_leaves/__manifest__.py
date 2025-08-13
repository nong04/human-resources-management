# /hr_leaves/__manifest__.py
{
    'name': 'Leave Management',
    'version': '17.0.1.0',
    'summary': 'Manage time off requests and allocations',
    'category': 'Human Resources/Time Off',
    'sequence': 2,
    'author': 'Do Thanh Long',
    'website': 'nong',
    'depends': [
        'hr_management',
        'mail',
    ],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'data/hr_leaves_data.xml',

        'views/hr_leaves_type_views.xml',
        'views/hr_leaves_request_views.xml',
        'views/hr_leaves_allocation_views.xml',
        'views/hr_employee_views.xml',

        'views/hr_leaves_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
