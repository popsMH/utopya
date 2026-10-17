import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { LoginScreen } from "@point_of_sale/app/screens/login_screen/login_screen";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    redirectToBackend() {
        window.location = "/odoo/home";
    },

    async onDeleteOrder(order) {
        if (order.get_orderlines().length > 0) {
            const confirmed = await ask(this.dialog, {
                title: _t("Cancel the current ticket"),
                body: _t(
                    "Are you sure you want to delete this ticket with a total amount of %s?",
                    this.env.utils.formatCurrency(order.get_total_with_tax())
                ),
                confirmLabel: _t("Yes, clear the ticket"),
                confirmClass: "btn-danger",
                cancelLabel: _t("Keep the ticket"),
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
        return _t("Main Menu");
    },
});
