# /payroll_attendance/models/payroll_payroll.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class PayrollPayroll(models.Model):
    _name = 'payroll.payroll'
    _description = 'Payroll'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_to desc'

    name = fields.Char(string='Name', required=True)
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)
    state = fields.Selection([('draft', 'Draft'), ('generated', 'Generated'), ('done', 'Done'),], string='Status', default='draft', tracking=True)
    slip_ids = fields.One2many('payroll.payslip', 'payroll_id', string='Payslips')
    payslip_count = fields.Integer(compute='_compute_payslip_count')
    selection_mode = fields.Selection([('employee', 'By Employee'), ('department', 'By Department'),],string="Selection Mode", default='employee', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    department_ids = fields.Many2many('hr.department', string='Departments')
    line_ids = fields.One2many('payroll.payroll.line', 'payroll_id', string='Payroll Bonuses & Deductions',
                               help="These rules will be used as a template to create initial lines on all generated payslips.")

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for payroll in self:
            if payroll.date_from > payroll.date_to:
                raise ValidationError(_("The start date of the payroll cannot be later than the end date."))

    @api.onchange('selection_mode')
    def _onchange_selection_mode(self):
        if self.selection_mode == 'employee' and not self.employee_ids:
            active_employees = self.env['hr.employee'].search([('work_status', '=', 'active')])
            self.employee_ids = active_employees
        elif self.selection_mode == 'department':
            self.employee_ids = [(5, 0, 0)]

    def _compute_payslip_count(self):
        for payroll in self:
            payroll.payslip_count = len(payroll.slip_ids)

    def action_generate_payslips(self):
        self.ensure_one()
        if self.slip_ids:
            raise UserError(_("Payslips have already been generated for this payroll. Please create a new payroll."))
        employees_to_generate = self.env['hr.employee']
        if self.selection_mode == 'employee':
            if not self.employee_ids:
                raise UserError(_("Please select at least one employee."))
            employees_to_generate = self.employee_ids
        elif self.selection_mode == 'department':
            if not self.department_ids:
                raise UserError(_("Please select at least one department."))
            employees_to_generate = self.env['hr.employee'].search([
                ('department_id', 'in', self.department_ids.ids),
                ('work_status', '=', 'active')
            ])
        if not employees_to_generate:
            raise UserError(_("No active employees found for the current selection."))
        payslip_vals_list = []
        for employee in employees_to_generate:
            payslip_vals_list.append({
                'employee_id': employee.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'payroll_id': self.id,
                'state': 'draft',
            })
        payslips = self.env['payroll.payslip'].create(payslip_vals_list)
        if self.line_ids:
            payslip_line_vals_list = []
            for slip in payslips:
                for payroll_line in self.line_ids:
                    payslip_line_vals_list.append({
                        'slip_id': slip.id,
                        'rule_id': payroll_line.rule_id.id,
                        'quantity': payroll_line.quantity,
                    })
            if payslip_line_vals_list:
                self.env['payroll.payslip.line'].create(payslip_line_vals_list)
        self.write({'state': 'generated'})
        return True

    def action_compute_all_sheets(self):
        self.slip_ids.action_compute_sheet()

    def action_confirm_all(self):
        self.slip_ids.action_set_to_done()
        self.write({'state': 'done'})

    def action_reset_to_draft(self):
        self.slip_ids.action_reset_to_draft()
        self.write({'state': 'generated'})

    def action_export_excel(self):
        self.ensure_one()
        done_slips = self.slip_ids.filtered(lambda slip: slip.state == 'done')
        if not done_slips:
            raise UserError(_("There are no 'Done' payslips in this payroll to export."))
        payslip_ids = done_slips.ids
        return {
            'type': 'ir.actions.act_url',
            'url': f'/payroll/export/payslips?ids={",".join(map(str, payslip_ids))}&payroll_id={self.id}',
            'target': 'self',
        }

    def action_view_payslips(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payslips of %s', self.name),
            'res_model': 'payroll.payslip',
            'view_mode': 'tree,form',
            'domain': [('payroll_id', '=', self.id)],
            'context': dict(self.env.context, create=False)
        }