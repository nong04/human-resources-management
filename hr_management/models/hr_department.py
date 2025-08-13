# /hr_management/models/hr_department.py

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrDepartment(models.Model):
    _name = 'hr.department'
    _description = 'Department'
    _inherit = ['mail.thread']
    _order = 'name'
    _parent_store = True

    name = fields.Char('Department Name', required=True)
    active = fields.Boolean('Active', default=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', tracking=True)
    parent_id = fields.Many2one('hr.department', string='Parent Department', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many('hr.department', 'parent_id', string='Child Departments')
    member_ids = fields.One2many('hr.employee', 'department_id', string='Members', readonly=True)
    employee_department_count = fields.Integer(compute='_compute_employee_department', string='Total Employees')

    @api.constrains('parent_id')
    def _check_department_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive departments.'))

    @api.constrains('manager_id')
    def _check_manager(self):
        for department in self:
            if department.manager_id and not department.manager_id.work_status == 'active':
                raise ValidationError(_("The manager of a department must be an active employee."))

    @api.depends('member_ids')
    def _compute_employee_department(self):
        for department in self:
            department.employee_department_count = len(department.member_ids)

    def action_open_employees(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Employees of {self.name}',
            'res_model': 'hr.employee',
            'view_mode': 'kanban,tree,form',
            'domain': [('department_id', '=', self.id)],
            'context': {'default_department_id': self.id}
        }