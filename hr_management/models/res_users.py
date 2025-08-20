# /hr_management/models/res_users.py
from odoo import fields, models, api

class Users(models.Model):
    _inherit = 'res.users'
    _HR_MANAGEMENT_WRITEABLE_FIELDS = [
        'work_phone', 'work_mobile', 'work_email', 'job_id', 'department_id', 'manager_id', 'coach_id',
        'work_location', 'resource_calendar_id', 'work_start_date', 'work_end_date',
        'private_address', 'phone', 'birthday', 'gender', 'nationality', 'identification_id', 'passport_id',
        'certificate', 'study_field', 'study_school',
    ]

    employee_ids = fields.One2many('hr.employee', 'user_id', string="Related Employees")
    employee_id = fields.Many2one(
        'hr.employee', string="Related Employee", compute='_compute_employee_id', store=False)
    #public
    work_phone = fields.Char(related='employee_id.work_phone', readonly=False, related_sudo=False)
    work_mobile = fields.Char(related='employee_id.work_mobile', readonly=False, related_sudo=False)
    work_email = fields.Char(related='employee_id.work_email', readonly=False, related_sudo=False)
    job_id = fields.Many2one(related='employee_id.job_id', readonly=False, related_sudo=False)
    department_id = fields.Many2one(related='employee_id.department_id', readonly=False, related_sudo=False)
    manager_id = fields.Many2one(related='employee_id.manager_id', readonly=False, related_sudo=False)
    coach_id = fields.Many2one(related='employee_id.coach_id', readonly=False, related_sudo=False)
    work_location = fields.Char(related='employee_id.work_location', readonly=False, related_sudo=False)
    resource_calendar_id = fields.Many2one(related='employee_id.resource_calendar_id', readonly=False, related_sudo=False)
    work_start_date = fields.Date(related='employee_id.work_start_date', readonly=False, related_sudo=False)
    work_end_date = fields.Date(related='employee_id.work_end_date', readonly=False, related_sudo=False)
    #private
    private_address = fields.Char(related='employee_id.private_address', readonly=False, related_sudo=False)
    phone = fields.Char(related='employee_id.phone', readonly=False, related_sudo=False)
    birthday = fields.Date(related='employee_id.birthday', readonly=False, related_sudo=False)
    gender = fields.Selection(related='employee_id.gender', readonly=False, related_sudo=False)
    nationality = fields.Many2one(related='employee_id.nationality', readonly=False, related_sudo=False)
    identification_id = fields.Char(related='employee_id.identification_id', readonly=False, related_sudo=False)
    passport_id = fields.Char(related='employee_id.passport_id', readonly=False, related_sudo=False)
    certificate = fields.Selection(related='employee_id.certificate', readonly=False, related_sudo=False)
    study_field = fields.Char(related='employee_id.study_field', readonly=False, related_sudo=False)
    study_school = fields.Char(related='employee_id.study_school', readonly=False, related_sudo=False)

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + self._HR_MANAGEMENT_WRITEABLE_FIELDS

    @api.depends('employee_ids')
    def _compute_employee_id(self):
        for user in self:
            user.employee_id = user.employee_ids[:1]

    @api.model
    def action_get(self):
        if self.env.user.employee_id:
            return self.env['ir.actions.act_window']._for_xml_id('hr_management.res_users_action_my_profile')
        return super(Users, self).action_get()

    def write(self, vals):
        res = super(Users, self).write(vals)
        if self.env.context.get('_no_employee_sync'):
            return res
        if any(key in vals for key in ['name', 'login', 'email', 'lang', 'tz', 'image_1920']):
            for user in self.filtered('employee_id'):
                employee_vals = {}
                if 'name' in vals and user.name != user.employee_id.name:
                    employee_vals['name'] = vals['name']
                if 'login' in vals and user.login != user.employee_id.work_email:
                    employee_vals['work_email'] = vals['login']
                if 'email' in vals and user.email != user.employee_id.email:
                    employee_vals['email'] = vals['email']
                if 'lang' in vals and user.lang != user.employee_id.language:
                    employee_vals['language'] = vals['lang']
                if 'tz' in vals and user.tz != user.employee_id.tz:
                    employee_vals['tz'] = vals['tz']
                if 'image_1920' in vals and user.image_1920 != user.employee_id.image_1920:
                    employee_vals['image_1920'] = vals['image_1920']
                if employee_vals:
                    user.employee_id.with_context(_no_user_sync=True).write(employee_vals)
        return res