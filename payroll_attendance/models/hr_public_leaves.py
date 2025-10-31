# /payroll_attendance/models/hr_public_leaves.py
from odoo import fields, models

class HrPublicLeaves(models.Model):
    _inherit = 'hr.public.leaves'

    public_leaves_rate = fields.Float(string="Public Leave Rate", default=1.0, help="Salary multiplier for working on this public leave. E.g., 3.0 for 300%.")