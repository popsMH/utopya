import { patch } from "@web/core/utils/patch";
import { OpeningControlPopup } from "@point_of_sale/app/store/opening_control_popup/opening_control_popup";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { parseFloat } from "@web/views/fields/parsers";

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
                title: "Fond de caisse requis",
                body: "Veuillez saisir un montant supérieur à 0,00 € pour ouvrir la caisse. Un fond de caisse est obligatoire pour garantir la fiabilité des clôtures comptables.",
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
