import { patch } from "@web/core/utils/patch";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { useState } from "@odoo/owl";

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

    // Traduit "Opening details:" en "Détail de l'ouverture :" dans la note affichée
    get displayOpeningNotes() {
        if (!this.props.opening_notes) {
            return this.props.opening_notes;
        }
        return this.props.opening_notes
            .replace(/Opening details:/g, "Détail du fond de caisse :")
            .replace(/Closing details:/g, "Détail de clôture :");
    },

    // Génère automatiquement le rapport de clôture avant de fermer la session
    async closeSession() {
        try {
            await this.downloadSalesReport();
        } catch {
            // Ne pas bloquer la fermeture si la génération du rapport échoue
        }
        return super.closeSession();
    },
});
