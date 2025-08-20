# /hr_leaves/models/hr_leaves_request.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_datetime
from datetime import datetime, time
import pytz

class HrLeavesRequest(models.Model):
    _name = 'hr.leaves.request'
    _description = 'Leave Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Description', compute='_compute_name', store=True, readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approve'),
        ('refused', 'Refused'),
        ('approved', 'Approved')],
        string='Status', tracking=True, copy=False, default='draft')
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, required=True, domain="[('work_status', '=', 'active')]")
    manager_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.manager_id', store=True)
    approver_id = fields.Many2one('res.users', string='Leave Approver', related='employee_id.leaves_manager_id', store=True)
    leaves_type_id = fields.Many2one('hr.leaves.type', string='Leave Type', required=True)
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    duration = fields.Float('Duration (Days)', compute='_compute_duration', store=True, help='Number of working days in the leave request.')
    reason = fields.Text('Reason')
    response = fields.Text('Response', help='Response from the approver.')
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')

    @api.depends('employee_id', 'leaves_type_id', 'duration')
    def _compute_name(self):
        for req in self:
            if req.employee_id and req.leaves_type_id:
                req.name = _("Leave Request for %(employee)s - %(type)s for %(duration)s day(s)",
                             employee=req.employee_id.name,
                             type=req.leaves_type_id.name,
                             duration=req.duration)
            else:
                req.name = _("New Leave Request")

    def _compute_can_approve(self):
        for request in self:
            is_manager = self.env.user.has_group('hr_leaves.group_hr_leaves_manager')
            is_own_manager = self.env.user == request.employee_id.leaves_manager_id
            request.can_approve = is_manager or is_own_manager

    def write(self, vals):
        if 'state' not in vals:
            if self.filtered(lambda r: r.state in ['approved', 'refused']):
                raise UserError(_("You cannot modify a request that has already been approved or refused."))
        res = super(HrLeavesRequest, self).write(vals)
        if any(field in vals for field in ['date_from', 'date_to', 'employee_id', 'state']):
            self._check_overlapping_leaves()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        requests = super().create(vals_list)
        requests._check_overlapping_leaves()
        return requests

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_duration(self):
        for request in self:
            if not request.date_from or not request.date_to or not request.employee_id:
                request.duration = 0
                continue
            if request.date_from > request.date_to:
                request.duration = 0
                continue
            public_leaves = self.env['hr.public.leaves'].get_public_leave_dates()
            calendar = request.employee_id.resource_calendar_id
            if not calendar:
                request.duration = (request.date_to - request.date_from).days + 1
                continue
            employee_tz = pytz.timezone(request.employee_id.tz or 'UTC')
            start_dt_naive = datetime.combine(request.date_from, time.min)
            end_dt_naive = datetime.combine(request.date_to, time.max)
            start_dt = employee_tz.localize(start_dt_naive)
            end_dt = employee_tz.localize(end_dt_naive)
            attendances = calendar._work_intervals_batch(start_dt, end_dt)[False]
            working_dates = set()
            for interval in attendances:
                interval_start_local = interval[0].astimezone(employee_tz)

                if interval_start_local.date() not in public_leaves:
                    working_dates.add(interval_start_local.date())

            request.duration = len(working_dates)

    def _check_overlapping_leaves(self):
        for request in self:
            if not request.employee_id or not request.date_from or not request.date_to or request.state != 'approved':
                continue

            domain = [
                ('employee_id', '=', request.employee_id.id),
                ('id', '!=', request.id),
                ('state', '=', 'approved'),
                ('date_to', '>=', request.date_from),
                ('date_from', '<=', request.date_to),
            ]

            overlapping_requests = self.search(domain)
            if overlapping_requests:
                raise ValidationError(_(
                    "You cannot have two approved leave requests that overlap. "
                    "This request for %(employee_name)s overlaps with: %(request_names)s",
                    employee_name=request.employee_id.name,
                    request_names=', '.join(overlapping_requests.mapped('name'))
                ))

    def _get_remaining_days(self):
        self.ensure_one()
        if self.leaves_type_id.requires_allocation == 'no':
            return float('inf')

        domain = [
            ('employee_id', '=', self.employee_id.id),
            ('leaves_type_id', '=', self.leaves_type_id.id),
            ('state', '=', 'approved'),
            ('date_from', '<=', self.date_to),
            '|',
            ('date_to', '>=', self.date_from),
            ('date_to', '=', False),
        ]

        allocation_data = self.env['hr.leaves.allocation']._read_group(domain, ['employee_id'], ['duration:sum'])
        total_allocated = allocation_data[0][1] if allocation_data else 0

        request_domain = [
            ('employee_id', '=', self.employee_id.id),
            ('leaves_type_id', '=', self.leaves_type_id.id),
            ('state', '=', 'approved'),
            ('id', '!=', self.id)
        ]

        request_data = self.env['hr.leaves.request']._read_group(request_domain, ['employee_id'], ['duration:sum'])
        total_taken = request_data[0][1] if request_data else 0

        return total_allocated - total_taken

    def action_confirm(self):
        self._check_overlapping_leaves()
        for request in self:
            if request.duration <= 0:
                raise ValidationError(
                    _("The duration of the leave must be at least one day (excluding public holidays and weekends)."))
            if request.leaves_type_id.requires_allocation == 'yes':
                remaining_days = request._get_remaining_days()
                if request.duration > remaining_days:
                    raise ValidationError(
                        _("You do not have enough remaining days for this leave type.\n"
                          "You have %(remaining)s days remaining, but you are requesting %(requested)s days.",
                          remaining=remaining_days, requested=request.duration)
                    )
            request.write({'state': 'confirm'})
            responsible = request.employee_id.leaves_manager_id or self.env.user
            request.activity_schedule('mail.mail_activity_data_todo', user_id=responsible.id)

    def action_approve(self):
        self._check_overlapping_leaves()
        response_msg = _("Leave Request approved by %(user)s on %(date)s",
                         user=self.env.user.name,
                         date=format_datetime(self.env, fields.Datetime.now()))
        self.write({'state': 'approved', 'approver_id': self.env.user.id, 'response': response_msg})
        self.message_post(body=response_msg)
        self.activity_feedback(['mail.mail_activity_data_todo'])

    def action_refuse(self):
        response_msg = _("Leave Request refused by %(user)s on %(date)s",
                         user=self.env.user.name,
                         date=format_datetime(self.env, fields.Datetime.now()))
        self.write({'state': 'refused', 'approver_id': self.env.user.id, 'response': response_msg})
        self.message_post(body=response_msg)
        self.activity_feedback(['mail.mail_activity_data_todo'])

    def action_draft(self):
        self.write({'state': 'draft', 'response': False})