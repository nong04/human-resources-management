# /payroll_attendance/models/attendance_record.py
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AttendanceRecord(models.Model):
    _name = 'payroll.attendance.record'
    _description = 'Attendance Record'
    _order = 'check_in desc'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
    check_in = fields.Datetime(string="Check In", required=True, default=fields.Datetime.now)
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)

    @api.constrains('employee_id', 'check_out')
    def _check_no_open_attendance(self):
        for record in self.filtered(lambda r: not r.check_out):
            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('check_out', '=', False),
                ('id', '!=', record.id),
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(_(
                    "The employee %(employee_name)s has an open attendance record. "
                    "Please check out the previous record before checking in again.",
                    employee_name=record.employee_id.name
                ))

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for record in self:
            if record.check_in and record.check_out:
                delta = record.check_out - record.check_in
                record.worked_hours = delta.total_seconds() / 3600.0
            else:
                record.worked_hours = 0.0

    @api.constrains('check_in', 'check_out')
    def _check_validity(self):
        for record in self:
            if record.check_in and record.check_out and record.check_out < record.check_in:
                raise ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))