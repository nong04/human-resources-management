# /hr_leaves/models/hr_leaves_type.py
from odoo import fields, models

class HrLeavesType(models.Model):
    _name = 'hr.leaves.type'
    _description = 'Time Off Type'
    _order = 'sequence, name'

    name = fields.Char(string='Time Off Type', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)

    requires_allocation = fields.Selection(
        [('yes', 'Yes'), ('no', 'No Required')],
        default='yes', required=True, string='Requires Allocation',
        help="""- Yes: Time off requests need to have a valid allocation.
        - No Limit: Time Off requests can be taken without any prior allocation.""")

    unpaid = fields.Boolean('Is Unpaid', default=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', "A time off type with the same name already exists.")
    ]