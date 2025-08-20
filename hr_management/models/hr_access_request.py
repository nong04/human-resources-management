# /hr_management/models/hr_access_request.py
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class HrAccessRequest(models.Model):
    _name = 'hr.access.request'
    _description = 'HR Access Level Request'
    _order = 'create_date desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, domain="[('user_id', '!=', False)]")
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', store=True, readonly=True)
    requested_level = fields.Selection([('user', 'User'), ('manager', 'Manager')], string='Requested Level', default='manager', required=True)
    state = fields.Selection([('confirm', 'To Approve'), ('approved', 'Approved'), ('refused', 'Refused')], string='Status', default='confirm', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            employee_id = vals.get('employee_id')
            requested_level = vals.get('requested_level')
            if employee_id and requested_level:
                self._validate_employee_access_request(employee_id, requested_level)
        return super(HrAccessRequest, self).create(vals_list)

    def write(self, vals):
        if 'employee_id' in vals or 'requested_level' in vals:
            for request in self:
                employee_id = vals.get('employee_id', request.employee_id.id)
                requested_level = vals.get('requested_level', request.requested_level)
                self._validate_employee_access_request(employee_id, requested_level)

        for request in self:
            if request.state in ['approved', 'refused']:
                raise UserError(_("You cannot modify a request that has already been approved or refused."))
        return super(HrAccessRequest, self).write(vals)

    def action_approve(self):
        for request in self:
            self._validate_request_state(request, 'confirm', 'approved')

            group_mapping = {
                'user': 'hr_management.group_hr_management_user',
                'manager': 'hr_management.group_hr_management_manager'
            }

            if request.user_id and request.requested_level in group_mapping:
                is_manager = request.user_id.has_group('hr_management.group_hr_management_manager')
                if request.requested_level == 'user' and is_manager:
                    manager_group = request.env.ref('hr_management.group_hr_management_manager')
                    manager_users = manager_group.users
                    if len(manager_users) <= 1:
                        raise UserError(_("Cannot approve this request. This user is the last manager in the system."))
                hr_groups = [request.env.ref(xml_id) for xml_id in group_mapping.values()]
                target_group = request.env.ref(group_mapping[request.requested_level])
                for group in hr_groups:
                    if group.id != target_group.id:
                        group.sudo().write({'users': [(3, request.user_id.id)]})
                target_group.sudo().write({'users': [(4, request.user_id.id)]})
                request.write({'state': 'approved'})
        return True

    def action_refuse(self):
        for request in self:
            self._validate_request_state(request, 'confirm', 'refused')
            request.write({'state': 'refused'})
        return True

    def _validate_employee_access_request(self, employee_id, requested_level):
        employee = self.env['hr.employee'].browse(employee_id)
        if not employee.user_id:
            raise UserError(_("The selected employee (%s) is not linked to a user account and cannot request access.", employee.name))

        is_manager = employee.user_id.has_group('hr_management.group_hr_management_manager')
        if (requested_level == 'manager' and is_manager) or (requested_level == 'user' and not is_manager):
            raise UserError(_("The user %s already has the requested access level.", employee.user_id.name))

        domain = [
            ('employee_id', '=', employee_id),
            ('state', '=','confirm')
        ]
        if self:
            domain.append(('id', '!=', self.id))
        existing_request = self.search(domain)
        if existing_request:
            raise UserError(_("There is already a pending access request for this employee. Please wait for it to be processed."))

    @staticmethod
    def _validate_request_state(request, expected_state, action_description):
        if request.state != expected_state:
            raise UserError(_("Only requests in '%s' state can be %s.", expected_state, action_description))