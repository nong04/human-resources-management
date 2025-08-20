# /hr_leaves/models/hr_public_leaves.py
from odoo import fields, models, _
from datetime import timedelta

class HrPublicLeaves(models.Model):
    _name = 'hr.public.leaves'
    _description = 'Public Leave'
    _order = 'date_from desc'

    name = fields.Char(string='Name', required=True)
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)

    _sql_constraints = [
        ('date_check', 'CHECK(date_from <= date_to)', 'The start date must be before or equal to the end date.')
    ]

    def get_public_leave_dates(self):
        public_dates = set()
        for public_leave in self.search([]):
            current_date = public_leave.date_from
            while current_date <= public_leave.date_to:
                public_dates.add(current_date)
                current_date += timedelta(days=1)
        return public_dates