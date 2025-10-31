# /hr_management/models/hr_employee.py
from importlib.metadata import requires

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _description = 'Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _order = 'name'

    # --- Thông tin chung ---
    name = fields.Char(string="Employee Name", related='resource_id.name', store=True, readonly=False, tracking=True)
    active = fields.Boolean('Active', related='resource_id.active', default=True, store=True, readonly=False,
                            help="Set active to false to hide the employee without removing it.")
    image_1920 = fields.Image("Image", max_width=1920, max_height=1920)
    is_manager = fields.Boolean(string="Is Manager", compute='_compute_is_manager')
    is_self = fields.Boolean(string="Is Self", compute='_compute_is_self')
    # --- Thông tin công việc ---
    work_email = fields.Char(string="Work Email", tracking=True)
    work_phone = fields.Char(string="Work Phone", tracking=True)
    work_mobile = fields.Char(string="Work Mobile", tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True, tracking=True)
    job_id = fields.Many2one('hr.job', string='Job Position', required=True, tracking=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', tracking=True)
    coach_id = fields.Many2one('hr.employee', string='Coach', tracking=True)
    work_location = fields.Char(string="Work Location", tracking=True, help="The physical location where the employee works.")
    work_start_date = fields.Date(string="Start Date", tracking=True)
    work_end_date = fields.Date(string="End Date", tracking=True)
    resource_calendar_id = fields.Many2one(
        'resource.calendar', 'Working Hours', default=lambda self: self.env.company.resource_calendar_id)
    tz = fields.Selection(string='Timezone', related='resource_id.tz', readonly=False,
        help="This field is used in order to define in which timezone the resources will work.")
    # --- Thông tin cá nhân ---
    private_address = fields.Char(string="Private Address", tracking=True)
    email = fields.Char(string="Private Email", tracking=True, required=True)
    phone = fields.Char(string="Private Phone", tracking=True)
    language = fields.Selection(
        selection='_get_language_selection', string="Language", default=lambda self: self.env.user.lang, required=True, tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender', tracking=True)
    birthday = fields.Date(string='Date of Birth', tracking=True, help="The employee's birth date. It should not be in the future.")
    nationality = fields.Many2one('res.country', string='Nationality', tracking=True)
    identification_id = fields.Char(string='Identification No', required=True, tracking=True)
    passport_id = fields.Char('Passport No', tracking=True)
    certificate = fields.Selection([
        ('graduate', 'Graduate'), ('bachelor', 'Bachelor'),
        ('master', 'Master'), ('doctor', 'Doctor'), ('other', 'Other')],
        'Certificate Level', default='other', tracking=True)
    study_field = fields.Char("Field of Study", tracking=True)
    study_school = fields.Char("School", tracking=True)
    # --- Cài đặt HR ---
    user_id = fields.Many2one('res.users', 'User', related='resource_id.user_id', store=True, readonly=False, ondelete='restrict')
    management_access_level = fields.Selection([('user', 'User'), ('manager', 'Manager')], string='Management',
        compute='_compute_management_access_level', inverse='_inverse_management_access_level', store=True, readonly=False, tracking=True)
    employee_type = fields.Selection([
        ('employee', 'Employee'), ('student', 'Student'), ('trainee', 'Trainee'),
        ('contractor', 'Contractor'), ('freelance', 'Freelancer')],
        string='Employee Type', default='employee', required=True, tracking=True)
    work_status = fields.Selection([('active', 'Active'), ('left', 'Left')], string="Work Status", default='active', tracking=True)

    _sql_constraints = [
        ('work_email_uniq', 'unique(work_email)', 'An employee work email must be unique.'),
        ('user_uniq', 'unique(user_id)', 'A user can only be linked to one employee.'),
        ('identification_id_uniq', 'unique(identification_id)', 'An employee identification number must be unique.'),
    ]

    @api.model
    def _get_language_selection(self):
        return self.env['res.lang'].get_installed()

    @api.constrains('birthday')
    def _check_birthday(self):
        for employee in self:
            if employee.birthday and employee.birthday > fields.Date.today():
                raise ValidationError(_("The employee's birth date cannot be in the future."))

    @api.constrains('manager_id', 'coach_id')
    def _check_manager_coach(self):
        for employee in self:
            if employee.manager_id and employee.manager_id == employee:
                raise ValidationError(_("An employee cannot be their own manager."))
            if employee.coach_id and employee.coach_id == employee:
                raise ValidationError(_("An employee cannot be their own coach."))

    @api.constrains('work_start_date', 'work_end_date')
    def _check_work_dates(self):
        for employee in self:
            if employee.work_start_date and employee.work_end_date and employee.work_end_date < employee.work_start_date:
                raise ValidationError(_("The work end date cannot be earlier than the start date."))

    @api.depends('user_id')
    @api.depends_context('uid')
    def _compute_is_manager(self):
        for employee in self:
            employee.is_manager = self.env.user.has_group('hr_management.group_hr_management_manager')

    @api.depends('user_id')
    @api.depends_context('uid')
    def _compute_is_self(self):
        for employee in self:
            employee.is_self = (employee.user_id and employee.user_id.id == self.env.uid) or (self.env.user.id == employee.user_id.id)

    @api.depends('user_id', 'user_id.groups_id')
    def _compute_management_access_level(self):
        manager_group = self.env.ref('hr_management.group_hr_management_manager', raise_if_not_found=False)
        if not manager_group:
            self.management_access_level = 'user'
            return
        manager_users = manager_group.users
        for employee in self:
            if employee.user_id and employee.user_id in manager_users:
                employee.management_access_level = 'manager'
            else:
                employee.management_access_level = 'user'

    @api.onchange('management_access_level')
    def _onchange_management_access_level(self):
        if not self._origin.id or not self.user_id:
            return
        is_current_user_manager = self.env.user.has_group('hr_management.group_hr_management_manager')
        if is_current_user_manager and self.user_id == self.env.user and self.management_access_level == 'user':
            return {
                'warning': {
                    'title': _("Confirmation"),
                    'message': _("You are about to change your own Management access level to User. You will lose your manager privileges upon saving."),
                }
            }

    def _inverse_management_access_level(self):
        if not self.env.user.has_group('hr_management.group_hr_management_manager'):
            raise AccessError(_("Only HR Managers can change Management access levels."))
        manager_group = self.env.ref('hr_management.group_hr_management_manager', raise_if_not_found=False)
        if not manager_group:
            return
        for employee in self:
            if not employee.user_id:
                continue
            is_last_manager = len(manager_group.users) == 1 and employee.user_id in manager_group.users
            if is_last_manager and employee.management_access_level == 'user':
                raise UserError(_("You cannot remove the last manager (%s) from the system.") % employee.name)
            if employee.management_access_level == 'manager':
                manager_group.sudo().users = [(4, employee.user_id.id)]
            else:
                manager_group.sudo().users = [(3, employee.user_id.id)]

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        if self.env['ir.config_parameter'].sudo().get_param('hr_management.auto_create_user'):
            employees.filtered(lambda e: e.work_email and not e.user_id)._create_user_from_employee()
        return employees

    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        if self.env.context.get('_no_user_sync'):
            return res
        for employee in self.filtered('user_id'):
            user_vals = {}
            if 'name' in vals and employee.name != employee.user_id.name:
                user_vals['name'] = vals['name']
            if 'work_email' in vals and employee.work_email != employee.user_id.login:
                user_vals['login'] = vals['work_email']
            if 'email' in vals and employee.email != employee.user_id.email:
                user_vals['email'] = vals['email']
            if 'language' in vals and employee.language != employee.user_id.lang:
                user_vals['lang'] = vals['language']
            if 'tz' in vals and employee.tz != employee.user_id.tz:
                user_vals['tz'] = vals['tz']
            if 'image_1920' in vals and employee.image_1920 != employee.user_id.image_1920:
                user_vals['image_1920'] = vals['image_1920']
            if user_vals:
                employee.user_id.sudo().with_context(_no_employee_sync=True).write(user_vals)
        return res

    def _create_user_from_employee(self):
        for employee in self:
            existing_user = self.env['res.users'].sudo().search([('login', '=', employee.work_email)], limit=1)
            if existing_user:
                employee.user_id = existing_user
                continue

            user_groups = [
                self.env.ref('base.group_user').id,
                self.env.ref('hr_management.group_hr_management_user').id
            ]
            user_vals = {
                'name': employee.name,
                'login': employee.work_email,
                'email': employee.email,
                'lang': employee.language,
                'tz': employee.tz,
                'groups_id': [(6, 0, user_groups)],
                'employee_ids': [(4, employee.id)]
            }
            try:
                user = self.env['res.users'].with_context(no_reset_password=True).sudo().create(user_vals)
                employee.user_id = user
            except Exception as e:
                _logger.error("Failed to create user for employee %s. Error: %s", employee.name, e)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.email = self.user_id.email if not self.email else self.email
            self.language = self.user_id.lang if not self.language else self.language
            self.tz = self.user_id.tz if not self.tz else self.tz
            self.image_1920 = self.user_id.image_1920 if not self.image_1920 else self.image_1920

    def action_related_user(self):
        self.ensure_one()
        if not self.user_id:
            raise UserError(_("This employee is not linked to any user."))
        action = self.env['ir.actions.act_window']._for_xml_id('hr_management.res_users_action_my_profile')
        action['res_id'] = self.user_id.id
        return action