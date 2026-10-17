import { patch } from "@web/core/utils/patch";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

patch(ClosePosPopup.prototype, {
    setup() {
        super.setup();
        this.qualiReparState = useState({ configured: false, total: 0, loaded: false });
        this._loadQualiReparTotal();
    },

    async _loadQualiReparTotal() {
        try {
            const data = await this.pos.data.call(
                "pos.session",
                "get_qualirepar_daily_total",
                [this.pos.session.id]
            );
            this.qualiReparState.configured = data.configured;
            this.qualiReparState.total = data.total;
        } catch {
            this.qualiReparState.configured = false;
            this.qualiReparState.total = 0;
        }
        this.qualiReparState.loaded = true;
    },

    // Relabel the system-generated "Opening details:" / "Closing details:" in the displayed note
    get displayOpeningNotes() {
        if (!this.props.opening_notes) {
            return this.props.opening_notes;
        }
        return this.props.opening_notes
            .replace(/Opening details:/g, _t("Opening cash details:"))
            .replace(/Closing details:/g, _t("Closing details:"));
    },

    // Automatically generate the closing report before closing the session
    async closeSession() {
        try {
            await this.downloadSalesReport();
        } catch {
            // Do not block closing if the report generation fails
        }
        return super.closeSession();
    },
});
