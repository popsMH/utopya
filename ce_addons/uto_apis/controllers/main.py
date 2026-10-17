from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
import requests
import logging


class EcologicAPI(http.Controller):

    @http.route('/api/get_repair_site', type='json', auth='public', methods=['GET'])
    def get_repair_site(self):
        """ Retrieve all ecologic sites """
        endpoint = "/api/v1/ecosupport/getrepairsitesbyats"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecologic_api_url")

        current_user = request.env.user
        user_company = current_user.company_id
        api_key = user_company.ecologic_api_key
        if not main_url or not api_key:
            raise ValidationError(_("Ecologic API Information is missing in the settings"))
        complete_url = main_url + endpoint
        # get_catalog call
        get_repair_site_headers = {
            "api_key": f"{api_key}",
            "Cache-Control": "no-cache"
        }
        res = requests.get(complete_url, headers=get_repair_site_headers, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Ecologic API error: %s") % res.text)


    @http.route('/api/get_brands', type='json', auth='public', methods=['GET'])
    def get_brands(self):
        """ Retrieve all Brands """
        endpoint = "/api/v1/ecosupport/printbrandlist"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecologic_api_url")
        
        current_user = request.env.user
        user_company = current_user.company_id
        api_key = user_company.ecologic_api_key

        if not main_url or not api_key:
            raise ValidationError(_("Ecologic API Information is missing in the settings"))
        complete_url = main_url + endpoint
        # get_catalog call
        get_brands_headers = {
            "api_key": f"{api_key}",
            "Cache-Control": "no-cache"
        }
        res = requests.get(complete_url, headers=get_brands_headers, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Ecologic API error: %s") % res.text)

    
    @http.route('/api/get_labeled_products', type='json', auth='public', methods=['GET'])
    def get_labeled_products(self):
        """ Retrieve all products """
        endpoint = "/api/v1/ecosupport/printproducttypewithlabellist"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecologic_api_url")
        
        current_user = request.env.user
        user_company = current_user.company_id
        api_key = user_company.ecologic_api_key

        if not main_url or not api_key:
            raise ValidationError(_("Ecologic API Information is missing in the settings"))
        complete_url = main_url + endpoint
        # get_catalog call
        get_brands_headers = {
            "api_key": f"{api_key}",
            "Cache-Control": "no-cache"
        }
        res = requests.get(complete_url, headers=get_brands_headers, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Ecologic API error: %s") % res.text)

    
    @http.route('/api/create_claim', type='json', auth='public', methods=['POST'])
    def create_claim(self):
        """ Create Claim """
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        endpoint = "/api/v1/ecosupport/createclaim"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecologic_api_url")

        current_user = request.env.user
        user_company = current_user.company_id
        api_key = user_company.ecologic_api_key

        if not main_url or not api_key:
            raise ValidationError(_("Ecologic API Information is missing in the settings"))
        complete_url = main_url + endpoint
        payload = data.json
        # create_claim call
        create_claim_headers = {
            "api_key": f"{api_key}",
            "Cache-Control": "no-cache"
        }
        raw_params = request.httprequest.args
        params = {
            "repairEndDate": raw_params.get('repairEndDate') or None,
            "repairSiteId": raw_params.get('repairSiteId') or None,
            "consumerInvoiceNumber": raw_params.get('consumerInvoiceNumber') or None,
            # "quoteNumber": "REF_INT_20240325-1" # optional
        }
        res = requests.post(complete_url, json=payload, headers=create_claim_headers, params=params, timeout=30)
        if res.status_code in [200, 206]:
            return res.json()
        else:
            raise Exception(_("Ecologic API error: %s") % res.text)

    
    @http.route('/api/attach_file', type='json', auth='public', methods=['POST'])
    def attach_file(self):
        """ Attach Claim Files """
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        endpoint = "/api/v1/ecosupport/AttachFile"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecologic_api_url")
        
        current_user = request.env.user
        user_company = current_user.company_id
        api_key = user_company.ecologic_api_key

        if not main_url or not api_key:
            raise ValidationError(_("Ecologic API Information is missing in the settings"))
        complete_url = main_url + endpoint
        payload = data.json
        # create_claim call
        create_claim_headers = {
            "api_key": f"{api_key}",
            "Cache-Control": "no-cache"
        }
        raw_params = request.httprequest.args
        params = {
            "ClaimId": raw_params.get('ClaimId') or None,
            "filename": raw_params.get('filename') or None,
            "fileextension": raw_params.get('fileextension') or None,
            "documentType": raw_params.get('documentType') or None,
        }
        res = requests.post(complete_url, json=payload, headers=create_claim_headers, params=params, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Ecologic API error: %s") % res.text)

    
    @http.route('/api/update_claim', type='json', auth='public', methods=['POST'])
    def update_claim(self):
        """ Update Claim Before submitting """
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        endpoint = "/api/v1/ecosupport/updateclaim"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecologic_api_url")
        
        current_user = request.env.user
        user_company = current_user.company_id
        api_key = user_company.ecologic_api_key

        if not main_url or not api_key:
            raise ValidationError(_("Ecologic API Information is missing in the settings"))
        complete_url = main_url + endpoint
        payload = data.json
        # update_claim call
        update_claim_headers = {
            "api_key": f"{api_key}",
            "Cache-Control": "no-cache"
        }
        raw_params = request.httprequest.args
        params = {
            "ClaimId": raw_params.get('ClaimId') or None,
            "repairEndDate": raw_params.get('repairEndDate') or None,
            "RepairSiteId": raw_params.get('repairSiteId') or None,
            "consumerInvoiceNumber": raw_params.get('consumerInvoiceNumber') or None,
        }
        res = requests.post(complete_url, json=payload, headers=update_claim_headers, params=params, timeout=30)
        if res.status_code in [200, 206]:
            return res.json()
        else:
            raise Exception(_("Ecologic API error: %s") % res.text)

    
    @http.route('/api/get_claim_status', type='json', auth='public', methods=['GET'])
    def get_claim_status(self):
        """ Check Claim Status """
        endpoint = "/api/v1/ecosupport/getclaimstatus"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecologic_api_url")
        
        current_user = request.env.user
        user_company = current_user.company_id
        api_key = user_company.ecologic_api_key

        if not main_url or not api_key:
            raise ValidationError(_("Ecologic API Information is missing in the settings"))
        complete_url = main_url + endpoint
        # get_catalog call
        get_claim_status_headers = {
            "api_key": f"{api_key}",
            "Cache-Control": "no-cache"
        }
        raw_params = request.httprequest.args
        params = {
            "ClaimId": raw_params.get('ClaimId') or None,
        }
        res = requests.get(complete_url, headers=get_claim_status_headers, params=params, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Ecologic API error: %s") % res.text)


class EcosystemAPI(http.Controller):
            
    @http.route('/api/login', type='json', auth='public', methods=['POST'])
    def login_api(self):
        """ Log in to ecosystem API to get token """
        endpoint = "/login"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecosystem_api_url")

        current_user = request.env.user
        user_company = current_user.company_id
        username = user_company.ecosystem_api_username
        password = user_company.ecosystem_api_password
        if not main_url or not username or not password:
            raise ValidationError(_("Ecosystem API Information is missing in the settings"))
        complete_url = main_url + endpoint
        body_vals = {
            "username": username,
            "password": password,
        }
        res = requests.post(complete_url, json=body_vals, timeout=30)
        return res.json()


    @http.route('/api/get_catalog', type='json', auth='public', methods=['GET'])
    def get_catalog(self):
        """ Retrieve all ecosystem catalog """
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        endpoint = "/catalog"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecosystem_api_url")
        if not main_url:
            raise ValidationError(_("Ecosystem API Information is missing in the settings"))
        complete_url = main_url + endpoint
        payload = data.json
        params = ""
        if payload:
            params = params + "?"
            query_string = "&".join(f"{k}={str(v).lower()}" for k, v in payload.items() if str(v).lower() == "true")
            params = params + query_string
        complete_url = complete_url + params
        # get_catalog call
        get_catalog_headers = {
            "Authorization": f"Bearer {payload['token']}",
        }
        res = requests.get(complete_url, headers=get_catalog_headers, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Ecosystem API error: %s") % res.text)


    @http.route('/api/new_claim', type='json', auth='public', methods=['POST'])
    def new_claim(self):
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        endpoint = "/reimbursement-claims/new_claim"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecosystem_api_url")
        if not main_url:
            raise ValidationError(_("Ecosystem API Information is missing in the settings"))
        complete_url = main_url + endpoint
        payload = data.json
        # new_claim call
        token = payload['token']
        new_claim_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        # Remove token key
        payload.pop("token", None)
        res = requests.post(complete_url, json=payload, headers=new_claim_headers, timeout=30)
        return res.json()

    
    @http.route('/api/reimbursement_claims/upload_file', type='json', auth='public', methods=['POST'])
    def reimbursement_claims_upload_file(self):
        """ Upload invoice (.pdf), serial_tag (.jpeg), claim_request (.png) and device_picture (.jpeg) """
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        endpoint = f"/reimbursement-claims/{payload['ReimbursementClaimID']}/upload-file"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecosystem_api_url")
        if not main_url:
            raise ValidationError(_("Ecosystem API Information is missing in the settings"))
        complete_url = main_url + endpoint
        # reimbursement_claims_upload_file call
        token = payload['token']
        upload_file_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        # Remove token key and ReimbursementClaimID key
        payload.pop("token", None)
        payload.pop("ReimbursementClaimID", None)
        res = requests.post(complete_url, json=payload, headers=upload_file_headers, timeout=30)
        if res.status_code == 201:
            return res.json()
        else:
            raise Exception(_("Ecosystem API error: %s") % res.text)


    # TODO: Put files to S3
    @http.route('/api/reimbursement_claims/put_files_s3', type='json', auth='public', methods=['POST'])
    def reimbursement_claims_put_files_s3(self):
        """ Put files to S3 """
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        endpoint = f"{payload['url']}"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecosystem_api_url")
        if not main_url:
            raise ValidationError(_("Ecosystem API Information is missing in the settings"))
        complete_url = main_url + endpoint
        # reimbursement_claims_put_files_s3 call
        res = requests.put(endpoint, timeout=30)
        if res.status_code == 200:
            return "put file OK"
        else:
            raise Exception(_("Ecosystem API error: %s") % res.text)


    @http.route('/api/reimbursement_claims/delete_claim', type='json', auth='public', methods=['POST'])
    def reimbursement_claims_delete_claim(self):
        """ Delete claim """
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        endpoint = f"/reimbursement-claims/{payload['ReimbursementClaimID']}"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecosystem_api_url")
        if not main_url:
            raise ValidationError(_("Ecosystem API Information is missing in the settings"))
        complete_url = main_url + endpoint
        # reimbursement_claims_delete_claim call
        token = payload['token']
        upload_file_headers = {
            "Authorization": f"Bearer {token}"
        }
        res = requests.delete(complete_url, headers=upload_file_headers, timeout=30)
        if res.status_code == 204:
            return {'result': 'deletion successful'}
        elif res.status_code in [201, 204]:
            return res.json()
        else:
            raise Exception(_("Ecosystem API error: %s") % res.text)

    
    @http.route('/api/reimbursement_claims/confirm_claim', type='json', auth='public', methods=['POST'])
    def reimbursement_claims_confirm_claim(self):
        """ Confirm claim """
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        endpoint = f"/reimbursement-claims/{payload['ReimbursementClaimID']}/confirm-claim"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecosystem_api_url")
        if not main_url:
            raise ValidationError(_("Ecosystem API Information is missing in the settings"))
        complete_url = main_url + endpoint
        # reimbursemenreimbursement_claims_confirm_claimt_claims_upload_file call
        token = payload['token']
        upload_file_headers = {
            "Authorization": f"Bearer {token}"
        }
        res = requests.post(complete_url, headers=upload_file_headers, timeout=30)
        if res.status_code == 201:
            return res.json()
        else:
            raise Exception(_("Ecosystem API error: %s") % res.text)

    
    @http.route('/api/reimbursement_claims/get_one_claim', type='json', auth='public', methods=['GET'])
    def reimbursement_claims_get_one_claim(self):
        """ Get one claim """
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        endpoint = f"/reimbursement-claims/{payload['ReimbursementClaimID']}"
        system_params = request.env["ir.config_parameter"].sudo()
        main_url = system_params.get_param("eco_api_config.ecosystem_api_url")
        if not main_url:
            raise ValidationError(_("Ecosystem API Information is missing in the settings"))
        complete_url = main_url + endpoint
        # reimbursement_claims_get_one_claim call
        token = payload['token']
        upload_file_headers = {
            "Authorization": f"Bearer {token}"
        }
        res = requests.get(complete_url, headers=upload_file_headers, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Ecosystem API error: %s") % res.text)