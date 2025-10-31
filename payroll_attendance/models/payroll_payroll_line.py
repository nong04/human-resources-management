# /payroll_attendance/models/payroll_payroll_line.py
from odoo import fields, models

class PayrollPayrollLine(models.Model):
    _name = 'payroll.payroll.line'
    _description = 'Payroll Bonus/Deduction Line'

    payroll_id = fields.Many2one('payroll.payroll', string="Payroll", required=True, ondelete='cascade')
    rule_id = fields.Many2one('payroll.bonus.deduction', string="Rule", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)