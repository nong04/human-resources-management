# /payroll_attendance/models/payroll_bonus_deduction.py
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class PayrollBonusDeduction(models.Model):
    _name = 'payroll.bonus.deduction'
    _description = 'Bonus and Deduction Rule'
    _order = 'sequence, id'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string="Sequence", default=10, help="Gives the order in which the rules are computed.")
    type = fields.Selection([('bonus', 'Bonus'), ('deduction', 'Deduction')], string="Type", required=True, default='bonus')
    computation_method = fields.Selection(
        [('fixed', 'Fixed Amount'), ('percentage', 'Percentage of Gross Salary')], string="Computation Method", required=True, default='fixed')
    currency_id = fields.Many2one('res.currency', compute='_compute_currency')
    currency_display_id = fields.Many2one('res.currency', compute='_compute_currency_display')
    amount_fixed = fields.Monetary(string="Fixed Amount (USD)", currency_field='currency_id')
    amount_fixed_display = fields.Monetary(
        string="Fixed Amount", compute='_compute_amount_fixed_display', inverse='_inverse_amount_fixed_display', currency_field='currency_display_id')
    amount_percentage = fields.Float(string="Percentage (%)")

    @api.constrains('amount_fixed', 'amount_percentage')
    def _check_positive_values(self):
        for rule in self:
            if rule.amount_fixed < 0:
                raise ValidationError(_("The fixed amount for a rule cannot be negative. Use the 'Type' field to set it as a deduction."))
            if rule.amount_percentage < 0:
                raise ValidationError(_("The percentage for a rule cannot be negative."))

    def _compute_currency(self):
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        for record in self:
            record.currency_id = usd_currency or self.env.company.currency_id

    def _compute_currency_display(self):
        param_sudo = self.env['ir.config_parameter'].sudo()
        currency_id_str = param_sudo.get_param('payroll_attendance.payroll_currency_id')
        default_currency = self.env.ref('base.USD', raise_if_not_found=False)
        display_currency = self.env['res.currency']
        if currency_id_str:
            display_currency = self.env['res.currency'].browse(int(currency_id_str))
        else:
            display_currency = self.env.company.currency_id or default_currency
        for record in self:
            record.currency_display_id = display_currency

    @api.depends('amount_fixed')
    def _compute_amount_fixed_display(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.amount_fixed_display = record.currency_id._convert(
                record.amount_fixed, record.currency_display_id, self.env.company, today)

    def _inverse_amount_fixed_display(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.amount_fixed = record.currency_display_id._convert(
                record.amount_fixed_display, record.currency_id, self.env.company, today)