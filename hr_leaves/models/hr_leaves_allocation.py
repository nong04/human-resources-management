# /hr_leaves/models/hr_leaves_allocation.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HrLeavesAllocation(models.Model):
    _name = 'hr.leaves.allocation'
    _description = 'Time Off Allocation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char('Description', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'To Approve'),
        ('refused', 'Refused'),
        ('approved', 'Approved')],
        string='Status', readonly=True, tracking=True, copy=False, default='draft')
    employee_id = fields.Many2one( 'hr.employee', string='Employee', index=True, required=True, domain="[('work_status', '=', 'active')]")
    leaves_type_id = fields.Many2one( 'hr.leaves.type', string='Time Off Type', required=True)
    duration = fields.Float( 'Duration (Days)', required=True, tracking=True, default=1, help='Duration in days.')

    def write(self, vals):
        for request in self:
            if request.state in ['approved', 'refused']:
                allowed_fields = {'message_follower_ids', 'activity_ids', 'message_ids'}
                if any(field not in allowed_fields for field in vals):
                    raise UserError(
                        _("You cannot modify a request that has already been approved or refused."))
        return super(HrLeavesAllocation, self).write(vals)

    @api.constrains('duration')
    def _check_duration(self):
        if any(allocation.duration <= 0 for allocation in self):
            raise ValidationError(_("The number of days must be greater than 0."))

    def action_submit(self):
        self.write({'state': 'confirm'})
        self.message_post(body=_("Request submitted for approval."))

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_refuse(self):
        self.write({'state': 'refused'})