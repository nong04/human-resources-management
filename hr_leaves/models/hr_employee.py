# /hr_leaves/models/hr_employee.py
from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    remaining_allocated_leaves_count = fields.Float('Remaining Leaves', compute='_compute_leaves_counts')

    def _compute_leaves_counts(self):
        allocated_leaves_types = self.env['hr.leaves.type'].search([('requires_allocation', '=', 'yes')])

        if not allocated_leaves_types:
            self.remaining_allocated_leaves_count = 0.0
            return

        allocation_data = self.env['hr.leaves.allocation']._read_group(
            [
                ('employee_id', 'in', self.ids),
                ('leaves_type_id', 'in', allocated_leaves_types.ids),
                ('state', '=', 'approved')
            ],
            ['employee_id'],
            ['duration:sum']
        )
        allocated_days = {employee.id: days for employee, days in allocation_data}

        leaves_data = self.env['hr.leaves.request']._read_group(
            [
                ('employee_id', 'in', self.ids),
                ('leaves_type_id', 'in', allocated_leaves_types.ids),
                ('state', '=', 'approved')
            ],
            ['employee_id'],
            ['duration:sum']
        )
        taken_days = {employee.id: days for employee, days in leaves_data}

        for employee in self:
            total_allocated = allocated_days.get(employee.id, 0.0)
            total_taken = taken_days.get(employee.id, 0.0)

            employee.remaining_allocated_leaves_count = total_allocated - total_taken

    def action_open_employee_allocations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f"{self.name}'s Allocations",
            'res_model': 'hr.leaves.allocation',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }