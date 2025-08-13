# /hr_leaves/models/hr_leaves_request.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HrLeavesRequest(models.Model):
    _name = 'hr.leaves.request'
    _description = 'Time Off Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc'

    employee_id = fields.Many2one( 'hr.employee', string='Employee', index=True, required=True, domain="[('work_status', '=', 'active')]")
    leaves_type_id = fields.Many2one( 'hr.leaves.type', string='Time Off Type', required=True)
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    duration = fields.Float( 'Duration (Days)', compute='_compute_duration', store=True, help='Number of days of the time off request.')
    notes= fields.Text('Reason')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'To Approve'),
        ('refused', 'Refused'),
        ('approved', 'Approved')],
        string='Status', tracking=True, default='draft')

    def write(self, vals):
        for request in self:
            if request.state in ['approved', 'refused']:
                allowed_fields = {'message_follower_ids', 'activity_ids', 'message_ids'}
                if any(field not in allowed_fields for field in vals):
                    raise UserError(
                        _("You cannot modify a request that has already been approved or refused."))
        return super(HrLeavesRequest, self).write(vals)

    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        """Compute the number of days for the time off request."""
        for request in self:
            if request.date_from and request.date_to:
                if request.date_from > request.date_to:
                    raise ValidationError(_('The start date must be before the end date.'))
                else:
                    delta = request.date_to - request.date_from
                    request.duration = delta.days + 1
            else:
                request.duration = 0

    def _compute_remaining_days(self, employee_id, leaves_type_id):
        """Calculate the remaining days for the employee and leave type."""
        if leaves_type_id.requires_allocation == 'no':
            return float('inf')

        allocations = self.env['hr.leaves.allocation'].search([
            ('employee_id', '=', employee_id.id),
            ('leaves_type_id', '=', leaves_type_id.id),
            ('state', '=', 'approved')
        ])
        total_allocated = sum(allocations.mapped('duration'))

        leaves_taken = self.search([
            ('employee_id', '=', employee_id.id),
            ('leaves_type_id', '=', leaves_type_id.id),
            ('state', '=', 'approved'),
            ('id', '!=', self.id)
        ])
        total_taken = sum(leaves_taken.mapped('duration'))

        return total_allocated - total_taken

    def action_submit(self):
        for request in self:
            if request.leaves_type_id.requires_allocation == 'yes':
                remaining_days = request._compute_remaining_days(request.employee_id, request.leaves_type_id)
                if request.duration > remaining_days:
                    raise ValidationError(
                        _("You do not have enough remaining days for this time off type.\n"
                          "You have %.2f days remaining, but you are requesting %.2f days.") %
                        (remaining_days, request.duration)
                    )
            request.write({'state': 'confirm'})
        self.message_post(body=_("Request submitted for approval."))

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_refuse(self):
        self.write({'state': 'refused'})