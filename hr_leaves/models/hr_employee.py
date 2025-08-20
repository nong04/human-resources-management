# /hr_leaves/models/hr_employee.py
from odoo import api, fields, models, _
from odoo.exceptions import AccessError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    remaining_leaves = fields.Float('Remaining Leaves', compute='_compute_remaining_leaves')
    leaves_manager_id = fields.Many2one('res.users', string='Leave Approver', compute='_compute_leaves_manager', store=True, readonly=False,
        help="User responsible for approving this employee's leave requests.")
    leaves_access_level = fields.Selection([('user', 'User'), ('manager', 'Manager')], string='Leaves',
        compute='_compute_leaves_access_level', inverse='_inverse_leaves_access_level', store=True, readonly=False, tracking=True)

    @api.depends('manager_id')
    def _compute_leaves_manager(self):
        for employee in self:
            if employee.manager_id and employee.manager_id.user_id:
                employee.leaves_manager_id = employee.manager_id.user_id
            else:
                employee.leaves_manager_id = False

    def _compute_remaining_leaves(self):
        allocated_leaves_types = self.env['hr.leaves.type'].search([('requires_allocation', '=', 'yes')])
        if not allocated_leaves_types:
            self.remaining_leaves = 0.0
            return

        domain = [
            ('employee_id', 'in', self.ids),
            ('leaves_type_id', 'in', allocated_leaves_types.ids),
            ('state', '=', 'approved')
        ]

        allocation_data = self.env['hr.leaves.allocation']._read_group(domain, ['employee_id'], ['duration:sum'])
        allocated_days = {employee.id: duration for employee, duration in allocation_data}

        leaves_data = self.env['hr.leaves.request']._read_group(domain, ['employee_id'], ['duration:sum'])
        taken_days = {employee.id: duration for employee, duration in leaves_data}

        for employee in self:
            total_allocated = allocated_days.get(employee.id, 0.0)
            total_taken = taken_days.get(employee.id, 0.0)
            employee.remaining_leaves = total_allocated - total_taken

    def action_open_my_leaves(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f"{self.name}'s Leaves",
            'res_model': 'hr.leaves.request',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }

    @api.depends('user_id', 'user_id.groups_id')
    def _compute_leaves_access_level(self):
        manager_group = self.env.ref('hr_leaves.group_hr_leaves_manager', raise_if_not_found=False)
        if not manager_group:
            self.leaves_access_level = 'user'
            return
        manager_users = manager_group.users
        for employee in self:
            if employee.user_id and employee.user_id in manager_users:
                employee.leaves_access_level = 'manager'
            else:
                employee.leaves_access_level = 'user'

    def _inverse_leaves_access_level(self):
        if not self.env.user.has_group('hr_leaves.group_hr_leaves_manager'):
            raise AccessError(_("Only Leave Managers can change Leaves access levels."))

        manager_group = self.env.ref('hr_leaves.group_hr_leaves_manager', raise_if_not_found=False)
        user_group = self.env.ref('hr_leaves.group_hr_leaves_user', raise_if_not_found=False)
        if not manager_group or not user_group:
            return

        for employee in self:
            if not employee.user_id:
                continue

            if not employee.user_id.has_group('hr_leaves.group_hr_leaves_user'):
                user_group.sudo().users = [(4, employee.user_id.id)]

            if employee.leaves_access_level == 'manager':
                manager_group.sudo().users = [(4, employee.user_id.id)]
            else:
                manager_group.sudo().users = [(3, employee.user_id.id)]