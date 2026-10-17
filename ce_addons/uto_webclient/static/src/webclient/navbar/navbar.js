import { _t } from "@web/core/l10n/translation";
import { patch } from '@web/core/utils/patch';
import { OmuxNavBar } from '@udoo_om_ux/webclient/navbar/navbar';
import { useService } from '@web/core/utils/hooks';
import { redirect } from "@web/core/utils/urls";
import { useState, onWillStart } from "@odoo/owl";


patch(OmuxNavBar.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.company = useService("company");
        this.companyCreateDate = useState({
            createDate: null,
            isPaid: null,
        });

        onWillStart(async () => {
            const companyId = this.company.currentCompany.id
            const currentCompanyId = await this.orm.searchRead("res.company", [['id', '=', companyId]], ["id", "name", "create_date"])
            this.companyCreateDate.createDate = new Date(currentCompanyId[0].create_date)
            // const today = new Date()
            // let diffDays
            // diffDays = Math.floor((today - this.companyCreateDate.createDate) / (1000 * 60 * 60 * 24))
            // if (diffDays < 0) {
            //     this.companyCreateDate.isExpired = true
            // }
            const isPaidStatus = await this.orm.call(
                'res.config.settings',
                'check_subscription_is_paid',
                [companyId]
            )
            this.companyCreateDate.isPaid = isPaidStatus.toString()
            console.log('akory aby')
        });
    },



    get expirationMessage() {
        const companyId = this.company.currentCompany.id
        
        // const currentCompanyInfos = this.getCompanyInfo(companyId)
        // const daysLeft = 15
        // const delay = _t("%s days", daysLeft);
        
        const createDate = this.companyCreateDate.createDate

        const today = new Date();
        let diffDays;
        if (createDate != null) {
            diffDays = Math.floor((today - createDate) / (1000 * 60 * 60 * 24));
        } else {
            diffDays = 16
        }
        // const diffDays = Math.floor((today - createDate) / (1000 * 60 * 60 * 24));
        // const daysLeft = Math.max(0, 15 - diffDays);
        const daysLeft = 15 - diffDays;
        const delay = _t("%s days", daysLeft);

        if (daysLeft == 0) {
            return ['is_zero', _t("This database expires today. ")];
        } else if (daysLeft < 0) {
            return ['is_negative', _t("This database has beed expired : %s. ", delay)];
        } else {
            return ['is_positive', _t("This database will expire in %s. ", delay)];
        }
    },

    async subscriptionPortalURL() {
        const companyId = this.company.currentCompany.id
        
        // const currentCompanyInfos = this.getCompanyInfo(companyId)
        const subscriptionUrl = await this.orm.call(
            'res.config.settings',
            'get_subscription_url',
            [companyId]
        );
        // redirect(subscriptionUrl);
        window.location.href = subscriptionUrl;
    },

    // async getCompanyInfo(companyId) {
    //     const domain = [['id', '=', companyId]]
    //     const currentCompanyId = await this.orm.searchRead("res.company", domain, ["id", "name", "create_date"])
    //     return currentCompanyId
    // },

});