import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

import { Component } from "@odoo/owl";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

class ResConfigTestConnection extends Component {
    static template = "res_config_test_connection";
    static props = {
        ...standardWidgetProps,
    };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");

    }

    async testConnection() {
        
        let result = await this.orm.call(
            'res.config.settings',
            'test_connection'
        )

        this.actionService.doAction({
            type: 'ir.actions.act_window',
            name: 'Connection',
            res_model: 'result.test.connection',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            context: {'default_result_message': result},
        })

    }
}

export const resConfigTestConnection = {
    component: ResConfigTestConnection,
};

registry.category("view_widgets").add("res_config_test_connection", resConfigTestConnection);
