# /hr_leaves/models/hr_leaves_calendar.py
from odoo import fields, models, tools

class HrLeavesCalendar(models.Model):
    _name = 'hr.leaves.calendar'
    _description = 'Overview of Leave Requests and Public Leaves'
    _auto = False

    name = fields.Char(string='Description', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    date_from = fields.Date(string='Start Date', readonly=True)
    date_to = fields.Date(string='End Date', readonly=True)
    type = fields.Selection([
        ('request', 'Leave Request'),
        ('public', 'Public Leaves')
    ], string='Type', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    req.id AS id,
                    req.name AS name,
                    req.employee_id AS employee_id,
                    req.date_from AS date_from,
                    req.date_to AS date_to,
                    'request' AS type
                FROM
                    hr_leaves_request req
                WHERE
                    req.state = 'approved'
            UNION ALL
                SELECT
                    (ph.id * -1) AS id,
                    ph.name AS name,
                    -1 AS employee_id,
                    ph.date_from AS date_from,
                    ph.date_to AS date_to,
                    'public' AS type
                FROM
                    hr_public_leaves ph
            )
        """ % (self._table,))