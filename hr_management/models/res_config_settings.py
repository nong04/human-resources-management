# /hr_management/models/res_config_settings.py
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_create_user_on_employee = fields.Boolean(
        string="Auto-Create User",
        help="Automatically create a user account when a new employee is created with a work email.",
        config_parameter='hr_management.auto_create_user',
        default=False,
    )