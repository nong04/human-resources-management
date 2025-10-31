# /payroll_attendance/models/res_config_settings.py
from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payroll_currency_id = fields.Many2one(
        'res.currency',
        string='Payroll Currency',
        config_parameter='payroll_attendance.payroll_currency_id',
        help="The currency used for all payroll calculations and records."
    )
    overtime_tolerance = fields.Integer(
        string="Overtime After (minutes)",
        config_parameter='payroll_attendance.overtime_tolerance',
        default=15,
        help="Work time is only considered overtime if it exceeds the standard hours by this many minutes."
    )
    undertime_tolerance = fields.Integer(
        string="Undertime After (minutes)",
        config_parameter='payroll_attendance.undertime_tolerance',
        default=15,
        help="Work time is only considered undertime if it's less than the standard hours by this many minutes."
    )
    payroll_overtime_rate = fields.Float(
        string="Overtime Rate",
        config_parameter='payroll_attendance.payroll_overtime_rate',
        default=1.5,
        help="Salary multiplier for overtime hours. E.g., 1.5 for 150%."
    )
    policy_paid_leave_allow_work = fields.Boolean(
        string="Allow Working on Paid Leave",
        config_parameter='payroll_attendance.policy_paid_leave_allow_work',
        default=False
    )
    policy_paid_leave_deduct_leave = fields.Boolean(
        string="Deduct Leave Day When Worked",
        config_parameter='payroll_attendance.policy_paid_leave_deduct_leave',
        default=True
    )
    policy_paid_leave_as_ot = fields.Boolean(
        string="Count as Overtime When Worked",
        config_parameter='payroll_attendance.policy_paid_leave_as_ot',
        default=False
    )
    policy_unpaid_leave_allow_work = fields.Boolean(
        string="Allow Working on Unpaid Leave",
        config_parameter='payroll_attendance.policy_unpaid_leave_allow_work',
        default=False
    )
    policy_unpaid_leave_as_ot = fields.Boolean(
        string="Count as Overtime When Worked",
        config_parameter='payroll_attendance.policy_unpaid_leave_as_ot',
        default=True
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        currency_id = params.get_param('payroll_attendance.payroll_currency_id')
        res.update(
            payroll_currency_id=int(currency_id) if currency_id else self.env.ref('base.USD').id,
        )
        return res