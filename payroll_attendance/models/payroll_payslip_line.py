# /payroll_attendance/models/payroll_payslip_line.py
from odoo import api, fields, models

class PayrollPayslipLine(models.Model):
    _name = 'payroll.payslip.line'
    _description = 'Payslip Bonus/Deduction Line'
    _order = 'sequence, id'

    slip_id = fields.Many2one('payroll.payslip', string="Payslip", required=True, ondelete='cascade')
    rule_id = fields.Many2one('payroll.bonus.deduction', string="Rule", required=True)
    sequence = fields.Integer(string="Sequence", related='rule_id.sequence', store=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    amount = fields.Monetary(string="Amount (USD)", readonly=True, store=True, currency_field='currency_id')
    amount_display = fields.Monetary(string="Amount", compute='_compute_amount_display', store=False, currency_field='currency_display_id')
    currency_id = fields.Many2one(related='slip_id.currency_id')
    currency_display_id = fields.Many2one(related='slip_id.currency_display_id')

    def _calculate_amount(self, base_amount):
        self.ensure_one()
        rule = self.rule_id
        amount_usd = 0.0
        if rule.computation_method == 'fixed':
            amount_usd = rule.amount_fixed * self.quantity
        elif rule.computation_method == 'percentage':
            amount_usd = (base_amount * rule.amount_percentage / 100) * self.quantity
        if rule.type == 'deduction':
            amount_usd = -amount_usd
        return amount_usd

    @api.depends('amount')
    def _compute_amount_display(self):
        for line in self:
            payslip = line.slip_id
            line.amount_display = payslip.currency_id._convert(
                line.amount, payslip.currency_display_id, self.env.company, payslip.date_to or fields.Date.today())