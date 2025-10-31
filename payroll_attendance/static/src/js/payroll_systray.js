/** @odoo-module **/
// /payroll_attendance/static/src/js/payroll_systray.js
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";
import { Dropdown } from '@web/core/dropdown/dropdown';
import { DropdownItem } from '@web/core/dropdown/dropdown_item';

class PayrollAttendanceSystray extends Component {
    static template = "payroll_attendance.PayrollAttendanceSystray";
    static components = { Dropdown, DropdownItem };
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            isEmployee: false,
            status: 'checked_out',
        });
        onWillStart(async () => {
            const systrayInfo = await this.orm.call(
                "hr.employee",
                "get_systray_info",
                []
            );
            this.state.isEmployee = systrayInfo.is_employee;
            if (systrayInfo.is_employee) {
                this.state.status = systrayInfo.status;
            }
        });
    }
    async onAttendanceChange() {
        const newState = await this.orm.call(
            "hr.employee",
            "action_manual_attendance",
            []
        );
        this.state.status = newState.status;
    }
}
export const payrollSystrayItem = {Component: PayrollAttendanceSystray,};
registry.category("systray").add("payroll_attendance.systray", payrollSystrayItem, {sequence: 25,});