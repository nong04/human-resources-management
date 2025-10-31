# /payroll_attendance/models/hr_employee.py
from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    currency_id = fields.Many2one('res.currency', compute='_compute_currency')
    currency_display_id = fields.Many2one('res.currency', compute='_compute_currency_display')
    base_salary = fields.Monetary(string="Base Salary (USD)", currency_field='currency_id', tracking=True)
    allowance = fields.Monetary(string="Allowance (USD)", currency_field='currency_id', tracking=True)
    base_salary_display = fields.Monetary(
        string="Base Salary", compute='_compute_display_fields', inverse='_inverse_base_salary_display', currency_field='currency_display_id')
    allowance_display = fields.Monetary(
        string="Allowance", compute='_compute_display_fields', inverse='_inverse_allowance_display', currency_field='currency_display_id')
    payroll_access_level = fields.Selection([('user', 'User'), ('manager', 'Manager')], string='Payroll',
                                            compute='_compute_payroll_access_level', inverse='_inverse_payroll_access_level',store=True, tracking=True)

    @api.constrains('base_salary', 'allowance')
    def _check_positive_salary(self):
        for employee in self:
            if employee.base_salary < 0:
                raise ValidationError(_("Base Salary cannot be negative."))
            if employee.allowance < 0:
                raise ValidationError(_("Allowance cannot be negative."))

    def _compute_currency(self):
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        for employee in self:
            employee.currency_id = usd_currency or self.env.company.currency_id

    def _compute_currency_display(self):
        param_sudo = self.env['ir.config_parameter'].sudo()
        currency_id_str = param_sudo.get_param('payroll_attendance.payroll_currency_id')
        default_currency = self.env.ref('base.USD', raise_if_not_found=False)
        display_currency = self.env['res.currency']
        if currency_id_str:
            display_currency = self.env['res.currency'].browse(int(currency_id_str))
        else:
            display_currency = self.env.company.currency_id or default_currency
        for employee in self:
            employee.currency_display_id = display_currency

    @api.depends('base_salary', 'allowance')
    def _compute_display_fields(self):
        today = fields.Date.context_today(self)
        for employee in self:
            employee.base_salary_display = employee.currency_id._convert(
                employee.base_salary, employee.currency_display_id, self.env.company, today)
            employee.allowance_display = employee.currency_id._convert(
                employee.allowance, employee.currency_display_id, self.env.company, today)

    def _inverse_base_salary_display(self):
        today = fields.Date.context_today(self)
        for employee in self:
            employee.base_salary = employee.currency_display_id._convert(
                employee.base_salary_display, employee.currency_id, self.env.company, today)

    def _inverse_allowance_display(self):
        today = fields.Date.context_today(self)
        for employee in self:
            employee.allowance = employee.currency_display_id._convert(
                employee.allowance_display, employee.currency_id, self.env.company, today)

    @api.depends('user_id', 'user_id.groups_id')
    def _compute_payroll_access_level(self):
        manager_group = self.env.ref('payroll_attendance.group_payroll_manager', raise_if_not_found=False)
        if not manager_group:
            self.payroll_access_level = 'user'
            return
        manager_users = manager_group.users
        for employee in self:
            if employee.user_id and employee.user_id in manager_users:
                employee.payroll_access_level = 'manager'
            else:
                employee.payroll_access_level = 'user'

    @api.onchange('payroll_access_level')
    def _onchange_payroll_access_level(self):
        if not self._origin.id or not self.user_id:
            return
        is_current_user_manager = self.env.user.has_group('payroll_attendance.group_payroll_manager')
        if is_current_user_manager and self.user_id == self.env.user and self.payroll_access_level == 'user':
            return {
                'warning': {
                    'title': _("Confirmation"),
                    'message': _(
                        "You are about to change your own Payroll access level to User. You will lose your manager privileges upon saving."),
                }
            }

    def _inverse_payroll_access_level(self):
        if not self.env.user.has_group('payroll_attendance.group_payroll_manager'):
            raise AccessError(_("Only Payroll Managers can change Payroll access levels."))
        manager_group = self.env.ref('payroll_attendance.group_payroll_manager', raise_if_not_found=False)
        user_group = self.env.ref('payroll_attendance.group_payroll_user', raise_if_not_found=False)
        if not manager_group or not user_group:
            return
        for employee in self:
            if not employee.user_id:
                continue
            is_last_manager = len(manager_group.users) == 1 and employee.user_id in manager_group.users
            if is_last_manager and employee.payroll_access_level == 'user':
                raise UserError(_("You cannot remove the last Payroll Manager (%s) from the system.") % employee.name)
            if not employee.user_id.has_group('payroll_attendance.group_payroll_user'):
                user_group.sudo().users = [(4, employee.user_id.id)]
            if employee.payroll_access_level == 'manager':
                manager_group.sudo().users = [(4, employee.user_id.id)]
            else:
                manager_group.sudo().users = [(3, employee.user_id.id)]

    @api.model
    def get_systray_info(self):
        employee = self.env.user.employee_id
        if not employee:
            return {'is_employee': False}
        last_attendance = self.env['payroll.attendance.record'].search([
            ('employee_id', '=', employee.id),
        ], order='check_in desc', limit=1)
        status = 'checked_out'
        last_attendance_id = False
        if last_attendance and not last_attendance.check_out:
            status = 'checked_in'
            last_attendance_id = last_attendance.id
        return {
            'is_employee': True,
            'status': status,
            'last_attendance_id': last_attendance_id,
        }

    @api.model
    def action_manual_attendance(self):
        employee = self.env.user.employee_id
        if not employee:
            raise UserError(_("You must be linked to an employee to use the attendance systray widget."))
        status_info = employee.get_systray_info()
        if status_info.get('status') == 'checked_out':
            self.env['payroll.attendance.record'].create({
                'employee_id': employee.id,
                'check_in': fields.Datetime.now(),
            })
        else:
            attendance = self.env['payroll.attendance.record'].browse(status_info.get('last_attendance_id'))
            if attendance:
                attendance.write({
                    'check_out': fields.Datetime.now(),
                })
        return employee.get_systray_info()