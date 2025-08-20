/** @odoo-module **/
// /hr_management/static/src/user_menu/my_profile.js

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { preferencesItem } from "@web/webclient/user_menu/user_menu_items";
/**
 * Override the user menu item for preferences to change its description.
 * @param {Object} env - The Odoo environment.
 * @returns {Object} The modified user menu item.
 */
export function hrManagementPreferencesItem(env) {
    const originalPreferencesItem = preferencesItem(env);
    return Object.assign({}, originalPreferencesItem, {description: _t('My Profile'),});
}
registry.category("user_menuitems").add('profile', hrManagementPreferencesItem, { force: true });