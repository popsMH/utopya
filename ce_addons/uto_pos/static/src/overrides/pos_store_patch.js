import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { LoginScreen } from "@point_of_sale/app/screens/login_screen/login_screen";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(PosStore.prototype, {
    redirectToBackend() {
        window.location = "/odoo/home";
    },

    async onDeleteOrder(order) {
        if (order.get_orderlines().length > 0) {
            const confirmed = await ask(this.dialog, {
                title: "Annuler le ticket en cours",
                body: `Êtes-vous sûr de vouloir supprimer ce ticket d'un montant total de ${this.env.utils.formatCurrency(order.get_total_with_tax())} ?`,
                confirmLabel: "Oui, vider le ticket",
                confirmClass: "btn-danger",
                cancelLabel: "Conserver le ticket",
            });
            if (!confirmed) {
                return false;
            }
        }
        const orderIsDeleted = await this.deleteOrders([order]);
        if (orderIsDeleted) {
            order.uiState.displayed = false;
            this.afterOrderDeletion();
        }
        return orderIsDeleted;
    },
});

patch(LoginScreen.prototype, {
    get backBtnName() {
        return "Menu Principal";
    },
});
