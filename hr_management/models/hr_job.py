# /hr_management/models/hr_job.py
from odoo import api, fields, models, _

class HrJob(models.Model):
    _name = 'hr.job'
    _description = 'Job Position'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(string='Job Position', required=True, translate=True)
    active = fields.Boolean(default=True)
    department_id = fields.Many2one('hr.department', string='Department')
    employee_ids = fields.One2many('hr.employee', 'job_id', string='Employees')
    employees_job_count = fields.Integer(string='Total Employees', compute='_compute_employee_job', store=True)

    _sql_constraints = [
        ('name_department_uniq', 'unique(name, department_id)',
         'The name of the job position must be unique per department!')
    ]

    @api.depends('employee_ids')
    def _compute_employee_job(self):
        employee_data = self.env['hr.employee']._read_group(
            [('job_id', 'in', self.ids)],
            ['job_id'],
            ['__count']
        )
        result = {job.id: count for job, count in employee_data}
        for job in self:
            job.employees_job_count = result.get(job.id, 0)

    def action_open_employees(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Employees in {self.name}',
            'res_model': 'hr.employee',
            'view_mode': 'kanban,tree,form',
            'domain': [('job_id', '=', self.id)],
            'context': {'default_job_id': self.id}
        }