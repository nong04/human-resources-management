# /hr_leaves/models/hr_leaves_allocation.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_datetime

class HrLeavesAllocation(models.Model):
    _name = 'hr.leaves.allocation'
    _description = 'Leave Allocation'
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
    leaves_type_id = fields.Many2one('hr.leaves.type', string='Leave Type', required=True, domain="[('requires_allocation', '=', 'yes')]")
    duration = fields.Float('Duration (Days)', required=True, tracking=True, default=1, help='Duration in days.')
    date_from = fields.Date('Valid From', required=True, tracking=True)
    date_to = fields.Date('Valid To', tracking=True)
    reason = fields.Text('Reason')
    response = fields.Text('Response', help='Response from the approver.')
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')

    @api.depends('employee_id', 'leaves_type_id', 'duration')
    def _compute_name(self):
        for alloc in self:
            if alloc.employee_id and alloc.leaves_type_id:
                alloc.name = _("Allocation Request for %(employee)s - %(type)s for %(duration)s day(s)",
                               employee=alloc.employee_id.name,
                               type=alloc.leaves_type_id.name,
                               duration=alloc.duration)
            else:
                alloc.name = _("New Allocation Request")

    def _compute_can_approve(self):
        for allocation in self:
            is_manager = self.env.user.has_group('hr_leaves.group_hr_leaves_manager')
            is_own_manager = self.env.user == allocation.employee_id.leaves_manager_id
            allocation.can_approve = is_manager or is_own_manager

    def write(self, vals):
        if 'state' not in vals:
            if self.filtered(lambda r: r.state in ['approved', 'refused']):
                raise UserError(_("You cannot modify an allocation that has already been approved or refused."))
        return super(HrLeavesAllocation, self).write(vals)

    @api.constrains('duration')
    def _check_duration(self):
        if any(allocation.duration <= 0 for allocation in self):
            raise ValidationError(_("The number of days must be greater than 0."))

    def action_confirm(self):
        self.write({'state': 'confirm'})
        for allocation in self.filtered(lambda hol: hol.state == 'confirm'):
            responsible = allocation.employee_id.leaves_manager_id or self.env.user
            self.activity_schedule('mail.mail_activity_data_todo', user_id=responsible.id)

    def action_approve(self):
        response_msg = _("Allocation Request approved by %(user)s on %(date)s",
                         user=self.env.user.name,
                         date=format_datetime(self.env, fields.Datetime.now()))
        self.write({'state': 'approved', 'approver_id': self.env.user.id, 'response': response_msg})
        self.message_post(body=response_msg)
        self.activity_feedback(['mail.mail_activity_data_todo'])

    def action_refuse(self):
        response_msg = _("Allocation Request refused by %(user)s on %(date)s",
                         user=self.env.user.name,
                         date=format_datetime(self.env, fields.Datetime.now()))
        self.write({'state': 'refused', 'approver_id': self.env.user.id, 'response': response_msg})
        self.message_post(body=response_msg)
        self.activity_feedback(['mail.mail_activity_data_todo'])

    def action_draft(self):
        self.write({'state': 'draft', 'response': False})
