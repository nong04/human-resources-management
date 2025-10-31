# /payroll_attendance/controllers/payroll_export.py
import io, re, xlsxwriter
from datetime import datetime
from odoo import http
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError

class PayrollExportController(http.Controller):

    @http.route('/payroll/export/payslips', type='http', auth='user')
    def export_payslips_excel(self, ids, **kw):
        payslip_ids = [int(i) for i in ids.split(',') if i]
        file_name_base = 'Payslip_Report'
        if kw.get('payroll_id'):
            try:
                b = request.env['payroll.payroll'].browse(int(kw['payroll_id']))
                if b.exists() and b.name:
                    file_name_base = re.sub(r'[^a-zA-Z0-9_-]', '_', b.name)
            except (ValueError, TypeError):
                pass
        file_name = f"{file_name_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        if not payslip_ids:
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            workbook.add_worksheet('Empty')
            workbook.close()
            output.seek(0)
            return request.make_response(
                output.read(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', content_disposition('Empty_Report.xlsx')),
                ],
            )
        payslips = request.env['payroll.payslip'].search([('id', 'in', payslip_ids),('state', '=', 'done'),])
        try:
            payslips.check_access_rule('read')
        except AccessError:
            return request.make_response("Access Denied.", status=403)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Payslips')
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D3D3D3'})
        currency_format = workbook.add_format({'num_format': f'#,##0.00 "{(payslips and payslips[0].currency_display_id or request.env.company.currency_id).symbol}"'})
        hours_format = workbook.add_format({'num_format': '0.00'})
        headers = ['Identification ID', 'Employee', 'Date From', 'Date To', 'Worked Hours', 'OT', 'Total Bonus', 'Total Deduction', 'Net Salary']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 18)
        for row, slip in enumerate(payslips, start=1):
            worksheet.write(row, 0, slip.identification_id or '')
            worksheet.write(row, 1, slip.employee_id.name)
            worksheet.write(row, 2, slip.date_from.strftime('%Y-%m-%d'))
            worksheet.write(row, 3, slip.date_to.strftime('%Y-%m-%d'))
            worksheet.write(row, 4, slip.actual_worked_hours + slip.paid_leaves_hours, hours_format)
            worksheet.write(row, 5, slip.overtime_hours + slip.public_leaves_worked_hours, hours_format)
            worksheet.write(row, 6, slip.total_bonus_display, currency_format)
            worksheet.write(row, 7, abs(slip.total_deduction_display), currency_format)
            worksheet.write(row, 8, slip.net_salary_display, currency_format)
        workbook.close()
        output.seek(0)
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(file_name)),
            ],
        )