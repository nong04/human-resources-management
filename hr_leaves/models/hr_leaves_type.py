# /hr_leaves/models/hr_leaves_type.py
from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class HrLeavesType(models.Model):
    _name = 'hr.leaves.type'
    _description = 'Leave Type'
    _order = 'sequence, name'

    name = fields.Char(string='Leave Type', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    requires_allocation = fields.Selection( [('yes', 'Yes'), ('no', 'No Limit')], default='yes', required=True, string='Requires Allocation',
        help="- Yes: Leave requests need to have a valid allocation.\n"
             "- No Limit: Leave requests can be taken without any prior allocation.")
    unpaid = fields.Boolean('Is Unpaid', default=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', "A leave type with the same name already exists.")
    ]

    def write(self, vals):
        if self.env.context.get('install_mode') or self.env.context.get('update_module'):
            return super().write(vals)
        disallowed = set(vals.keys()) - {'sequence'}
        if disallowed:
            raise ValidationError(_("Editing existing leave types is not allowed. You can create or delete records instead."))
        return super().write(vals)