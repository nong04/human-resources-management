# /payroll_attendance/models/payroll_payslip.py
import logging
from datetime import date, datetime, time
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict

_logger = logging.getLogger(__name__)

class PayrollPayslip(models.Model):
    _name = 'payroll.payslip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_to desc'

    is_manager = fields.Boolean(string="Is Payroll Manager", compute='_compute_is_manager')
    # Currency Fields
    currency_id = fields.Many2one('res.currency', compute='_compute_currency')
    currency_display_id = fields.Many2one('res.currency', string="Currency", compute='_compute_currency_display', store=True)
    # Storage Fields (in USD)
    hourly_wage = fields.Monetary(readonly=True, currency_field='currency_id')
    base_pay = fields.Monetary(readonly=True, currency_field='currency_id')
    overtime_pay = fields.Monetary(readonly=True, currency_field='currency_id')
    public_leaves_pay = fields.Monetary(string="Public Leaves Pay (USD)", readonly=True, currency_field='currency_id')
    allowance = fields.Monetary(readonly=True, currency_field='currency_id')
    total_bonus = fields.Monetary(compute='_compute_adjustments', store=True, currency_field='currency_id')
    total_deduction = fields.Monetary(compute='_compute_adjustments', store=True, currency_field='currency_id')
    gross_salary_before_adjustments = fields.Monetary(compute='_compute_gross_salary', store=True, currency_field='currency_id')
    net_salary = fields.Monetary(compute='_compute_net_salary', store=True, currency_field='currency_id')
    # Display Fields (in Display Currency)
    hourly_wage_display = fields.Monetary(string="Hourly Wage", compute='_compute_display_fields', currency_field='currency_display_id')
    net_salary_display = fields.Monetary(string="Net Salary", compute='_compute_display_fields', currency_field='currency_display_id')
    gross_salary_display = fields.Monetary(string="Gross Salary (Before Adj.)", compute='_compute_display_fields', currency_field='currency_display_id')
    total_bonus_display = fields.Monetary(string="Total Bonus", compute='_compute_display_fields', currency_field='currency_display_id')
    total_deduction_display = fields.Monetary(string="Total Deduction", compute='_compute_display_fields', currency_field='currency_display_id')
    base_pay_display = fields.Monetary(string="Base Pay", compute='_compute_display_fields', currency_field='currency_display_id')
    overtime_pay_display = fields.Monetary(string="Overtime Pay", compute='_compute_display_fields', currency_field='currency_display_id')
    public_leaves_pay_display = fields.Monetary(string="Public Leaves Pay", compute='_compute_display_fields', currency_field='currency_display_id')
    allowance_display = fields.Monetary(string="Allowance", compute='_compute_display_fields', currency_field='currency_display_id')
    # Other fields
    name = fields.Char(string='Description', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date_from = fields.Date(string='From', required=True, default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(string='To', required=True, default=lambda self: date.today())
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', default='draft', tracking=True)
    payroll_id = fields.Many2one('payroll.payroll', string='Payroll', ondelete='cascade')
    identification_id = fields.Char(related='employee_id.identification_id', string="Identification No", store=True, readonly=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string="Department", store=True, readonly=True)
    resource_calendar_id = fields.Many2one(
        'resource.calendar', related='employee_id.resource_calendar_id', string="Working Schedule", store=True, readonly=True)
    # Hour Calculation Fields
    standard_work_hours = fields.Float(string="Standard Hours", readonly=True)
    actual_worked_hours = fields.Float(string="Actual Worked Hours", readonly=True)
    paid_leaves_hours = fields.Float(string="Paid Leave Hours", readonly=True)
    overtime_hours = fields.Float(string="Overtime Hours", readonly=True)
    public_leaves_worked_hours = fields.Float(string="Public Leaves Worked Hours", readonly=True)
    unpaid_leaves_hours = fields.Float(string="Unpaid Leave Hours", readonly=True)
    line_ids = fields.One2many('payroll.payslip.line', 'slip_id', string="Bonuses & Deductions")

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for slip in self:
            if slip.date_from > slip.date_to:
                raise ValidationError(_("The start date of the payslip cannot be later than the end date."))

    @api.constrains('employee_id', 'date_from', 'date_to')
    def _check_employee_contract_dates(self):
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue
            employee = slip.employee_id
            if employee.work_start_date and slip.date_to < employee.work_start_date:
                raise ValidationError(_(
                    "The payslip period (ending on %(slip_end)s) is completely before the employee's start date (%(emp_start)s).",
                    slip_end=slip.date_to, emp_start=employee.work_start_date
                ))
            if employee.work_end_date and slip.date_from > employee.work_end_date:
                raise ValidationError(_(
                    "The payslip period (starting on %(slip_start)s) is completely after the employee's end date (%(emp_end)s).",
                    slip_start=slip.date_from, emp_end=employee.work_end_date
                ))

    @api.depends('employee_id')
    @api.depends_context('uid')
    def _compute_is_manager(self):
        is_manager_access = self.env.user.has_group('payroll_attendance.group_payroll_manager')
        for slip in self:
            slip.is_manager = is_manager_access

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_name(self):
        for slip in self:
            if slip.employee_id and slip.date_from and slip.date_to:
                slip.name = _("%s: %s - %s") % (slip.employee_id.name, slip.date_from, slip.date_to)
            else:
                slip.name = _("New Payslip")

    def _compute_currency(self):
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        for slip in self:
            slip.currency_id = usd_currency or self.env.company.currency_id

    @api.depends('employee_id')
    def _compute_currency_display(self):
        param_sudo = self.env['ir.config_parameter'].sudo()
        currency_id_str = param_sudo.get_param('payroll_attendance.payroll_currency_id')
        default_currency = self.env.ref('base.USD', raise_if_not_found=False)
        display_currency = self.env['res.currency']
        if currency_id_str:
            display_currency = self.env['res.currency'].browse(int(currency_id_str))
        else:
            display_currency = self.env.company.currency_id or default_currency
        for slip in self:
            slip.currency_display_id = display_currency

    @api.depends('net_salary', 'gross_salary_before_adjustments', 'total_bonus', 'total_deduction', 'base_pay', 'overtime_pay', 'public_leaves_pay', 'allowance')
    def _compute_display_fields(self):
        for slip in self:
            date = slip.date_to or fields.Date.today()
            company = self.env.company
            from_curr = slip.currency_id
            to_curr = slip.currency_display_id
            slip.hourly_wage_display = from_curr._convert(slip.hourly_wage, to_curr, company, date)
            slip.net_salary_display = from_curr._convert(slip.net_salary, to_curr, company, date)
            slip.gross_salary_display = from_curr._convert(slip.gross_salary_before_adjustments, to_curr, company, date)
            slip.total_bonus_display = from_curr._convert(slip.total_bonus, to_curr, company, date)
            slip.total_deduction_display = from_curr._convert(slip.total_deduction, to_curr, company, date)
            slip.base_pay_display = from_curr._convert(slip.base_pay, to_curr, company, date)
            slip.overtime_pay_display = from_curr._convert(slip.overtime_pay, to_curr, company, date)
            slip.public_leaves_pay_display = from_curr._convert(slip.public_leaves_pay, to_curr, company, date)
            slip.allowance_display = from_curr._convert(slip.allowance, to_curr, company, date)

    @api.depends('line_ids', 'gross_salary_before_adjustments')
    def _compute_adjustments(self):
        for slip in self:
            current_gross = slip.gross_salary_before_adjustments
            total_bonus = 0.0
            total_deduction = 0.0
            for line in slip.line_ids.sorted('sequence'):
                line_amount = line._calculate_amount(current_gross)
                if line.amount != line_amount:
                    line.with_context(force_write=True).write({'amount': line_amount})
                if line_amount > 0:
                    total_bonus += line_amount
                    current_gross += line_amount
                else:
                    total_deduction += line_amount
            slip.total_bonus = total_bonus
            slip.total_deduction = total_deduction

    @api.depends('base_pay', 'overtime_pay', 'public_leaves_pay', 'allowance')
    def _compute_gross_salary(self):
        for slip in self:
            slip.gross_salary_before_adjustments = slip.base_pay + slip.overtime_pay + slip.public_leaves_pay + slip.allowance

    @api.depends('gross_salary_before_adjustments', 'total_bonus', 'total_deduction')
    def _compute_net_salary(self):
        for slip in self:
            slip.net_salary = slip.gross_salary_before_adjustments + slip.total_bonus + slip.total_deduction

    @api.constrains('employee_id', 'date_from', 'date_to')
    def _check_overlapping_payslips(self):
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue
            domain = [
                ('employee_id', '=', slip.employee_id.id),
                ('id', '!=', slip.id),
                ('date_to', '>=', slip.date_from),
                ('date_from', '<=', slip.date_to),
            ]
            overlapping_payslips = self.search(domain, limit=1)
            if overlapping_payslips:
                raise ValidationError(_(
                    "You cannot create overlapping payslips for the same employee. "
                    "The period for %(employee_name)s (from %(start_date)s to %(end_date)s) "
                    "overlaps with the existing payslip: %(existing_slip)s.",
                    employee_name=slip.employee_id.name, start_date=slip.date_from, end_date=slip.date_to, existing_slip=overlapping_payslips.name
                ))

    def action_compute_sheet(self):
        params = self.env['ir.config_parameter'].sudo()
        ot_tolerance = int(params.get_param('payroll_attendance.overtime_tolerance', 15))
        ot_rate = float(params.get_param('payroll_attendance.payroll_overtime_rate', 1.5))
        policy_paid_allow = params.get_param('payroll_attendance.policy_paid_leave_allow_work', 'False') == 'True'
        policy_paid_as_ot = params.get_param('payroll_attendance.policy_paid_leave_as_ot', 'False') == 'True'
        policy_unpaid_allow = params.get_param('payroll_attendance.policy_unpaid_leave_allow_work', 'False') == 'True'
        policy_unpaid_as_ot = params.get_param('payroll_attendance.policy_unpaid_leave_as_ot', 'True') == 'True'
        for slip in self:
            employee = slip.employee_id
            if employee.base_salary <= 0:
                raise UserError(_("Cannot compute payslip. Employee '%s' does not have a valid base salary defined.", employee.name))
            calendar = employee.resource_calendar_id
            if not calendar:
                raise UserError(_("Employee '%s' has no working calendar.", employee.name))
            employee_tz = pytz.timezone(employee.tz or 'UTC')
            start_date_naive = datetime.combine(slip.date_from, time.min)
            end_date_naive = datetime.combine(slip.date_to, time.max)
            start_dt_local = employee_tz.localize(start_date_naive)
            end_dt_local = employee_tz.localize(end_date_naive)
            start_dt_utc = start_dt_local.astimezone(pytz.utc)
            end_dt_utc = end_dt_local.astimezone(pytz.utc)
            public_leaves_records = self.env['hr.public.leaves'].search([
                ('date_from', '<=', slip.date_to), ('date_to', '>=', slip.date_from)
            ])
            public_leaves = {}
            for record in public_leaves_records:
                for d in record.get_public_leave_dates():
                    public_leaves[d] = record
            approved_leaves = self.env['hr.leaves.request'].search([
                ('employee_id', '=', employee.id), ('state', '=', 'approved'),
                ('date_from', '<=', slip.date_to), ('date_to', '>=', slip.date_from)
            ])
            def get_dates_in_range(start_date, end_date):
                from datetime import timedelta
                current_date = start_date
                while current_date <= end_date:
                    yield current_date
                    current_date += timedelta(days=1)
            paid_leaves_dates = {
                d for leave in approved_leaves if not leave.leaves_type_id.unpaid
                for d in get_dates_in_range(leave.date_from, leave.date_to)
            }
            unpaid_leaves_dates = {
                d for leave in approved_leaves if leave.leaves_type_id.unpaid
                for d in get_dates_in_range(leave.date_from, leave.date_to)
            }
            attendances = self.env['payroll.attendance.record'].search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', start_dt_utc.replace(tzinfo=None)),
                ('check_out', '<=', end_dt_utc.replace(tzinfo=None))
            ])
            work_intervals = calendar._work_intervals_batch(start_dt_utc, end_dt_utc, resources=employee.resource_id)
            standard_hours = 0
            for interval in work_intervals.get(employee.resource_id.id, []):
                interval_date = interval[0].astimezone(employee_tz).date()
                if interval_date not in public_leaves:
                    standard_hours += (interval[1] - interval[0]).total_seconds() / 3600
            hourly_wage = (employee.base_salary / standard_hours) if standard_hours > 0 else 0
            actual_hours, ot_hours, public_leaves_worked_hours = 0, 0, 0
            paid_hours_not_worked, unpaid_hours = 0, 0
            total_public_leaves_pay = 0
            attendances_by_day = defaultdict(list)
            for att in attendances:
                local_check_in_date = att.check_in.astimezone(employee_tz).date()
                attendances_by_day[local_check_in_date].append(att)
            for day, day_attendances in attendances_by_day.items():
                worked_on_day = sum(att.worked_hours for att in day_attendances)
                if day in public_leaves:
                    public_leaves_worked_hours += worked_on_day
                    leaves_record = public_leaves[day]
                    total_public_leaves_pay += worked_on_day * hourly_wage * leaves_record.public_leaves_rate
                    continue
                day_start_local = employee_tz.localize(datetime.combine(day, time.min))
                day_end_local = employee_tz.localize(datetime.combine(day, time.max))
                day_work_intervals = calendar._work_intervals_batch(
                    day_start_local.astimezone(pytz.utc), day_end_local.astimezone(pytz.utc),
                    resources=employee.resource_id
                )
                standard_hours_on_day = sum(
                    (i[1] - i[0]).total_seconds() / 3600 for i in day_work_intervals.get(employee.resource_id.id, []))
                if not standard_hours_on_day > 0:
                    ot_hours += worked_on_day
                    continue
                if day in paid_leaves_dates:
                    if not policy_paid_allow:
                        raise UserError(
                            _("Employee %s worked on %s which was an approved paid leave day. This is not allowed by current policy.",
                              employee.name, day))
                    if policy_paid_as_ot:
                        ot_hours += worked_on_day
                    else:
                        actual_hours += worked_on_day
                    continue
                if day in unpaid_leaves_dates:
                    if not policy_unpaid_allow:
                        raise UserError(
                            _("Employee %s worked on %s which was an approved unpaid leave day. This is not allowed by current policy.",
                              employee.name, day))
                    if policy_unpaid_as_ot:
                        ot_hours += worked_on_day
                    else:
                        actual_hours += worked_on_day
                    continue
                overtime_on_day = worked_on_day - standard_hours_on_day
                if overtime_on_day * 60 > ot_tolerance:
                    ot_hours += overtime_on_day
                    actual_hours += standard_hours_on_day
                else:
                    actual_hours += worked_on_day
            policy_paid_deduct = params.get_param('payroll_attendance.policy_paid_leave_deduct_leave', 'True') == 'True'
            all_leave_dates_in_period = paid_leaves_dates.union(unpaid_leaves_dates)
            for leave_date in all_leave_dates_in_period:
                if leave_date not in attendances_by_day and leave_date not in public_leaves:
                    day_start_local = employee_tz.localize(datetime.combine(leave_date, time.min))
                    day_end_local = employee_tz.localize(datetime.combine(leave_date, time.max))
                    day_work_intervals = calendar._work_intervals_batch(
                        day_start_local.astimezone(pytz.utc), day_end_local.astimezone(pytz.utc),
                        resources=employee.resource_id
                    )
                    standard_hours_on_day = sum(
                        (i[1] - i[0]).total_seconds() / 3600 for i in
                        day_work_intervals.get(employee.resource_id.id, []))
                    if standard_hours_on_day > 0:
                        if leave_date in paid_leaves_dates and policy_paid_deduct:
                            paid_hours_not_worked += standard_hours_on_day
                        elif leave_date in unpaid_leaves_dates:
                            unpaid_hours += standard_hours_on_day
            slip.write({
                'standard_work_hours': standard_hours,
                'hourly_wage': hourly_wage,
                'actual_worked_hours': actual_hours,
                'overtime_hours': ot_hours,
                'public_leaves_worked_hours': public_leaves_worked_hours,
                'paid_leaves_hours': paid_hours_not_worked,
                'unpaid_leaves_hours': unpaid_hours,
                'allowance': employee.allowance,
                'base_pay': min(actual_hours + paid_hours_not_worked, standard_hours) * hourly_wage,
                'overtime_pay': ot_hours * hourly_wage * ot_rate,
                'public_leaves_pay': total_public_leaves_pay,
            })
        return True

    def action_set_to_done(self):
        self.write({'state': 'done'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})