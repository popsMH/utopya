import { patch } from "@web/core/utils/patch";
import { OpeningControlPopup } from "@point_of_sale/app/store/opening_control_popup/opening_control_popup";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { parseFloat } from "@web/views/fields/parsers";
import { _t } from "@web/core/l10n/translation";

patch(OpeningControlPopup.prototype, {
    setup() {
        super.setup();
        this._onKeyDown = this._handleEnterKey.bind(this);
        onMounted(() => document.addEventListener("keydown", this._onKeyDown));
        onWillUnmount(() => document.removeEventListener("keydown", this._onKeyDown));
    },

    async confirm() {
        if (parseFloat(this.state.openingCash) === 0) {
            this.dialog.add(AlertDialog, {
                title: _t("Opening cash required"),
                body: _t("Please enter an amount greater than €0.00 to open the register. An opening cash amount is required to ensure reliable accounting closings."),
            });
            return;
        }
        return super.confirm();
    },

    _handleEnterKey(ev) {
        if (ev.key === "Enter" && this.env.utils.isValidFloat(this.state.openingCash)) {
            this.confirm();
        }
    },
});
