# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#
import time

from connect.client.exceptions import ClientError
from connect.eaas.extension import (
    Extension,
    ProcessingResponse,
    ProductActionResponse,
)

from jwt import encode


class IdeasPortalExtension(Extension):

    DEFAULT_REDIRECT = 'https://ingrammicrocloud.com'
    DEFAULT_EXPIRATION_MINUTES = 1

    def _calculate_aha_token(self, data, jwt_payload):
        expiration_mins = self.config.get("TOKEN_EXP_MINUTES", self.DEFAULT_EXPIRATION_MINUTES)

        payload = {}
        payload['iat'] = int(time.time())
        payload['jti'] = jwt_payload['asset_id']
        payload['first_name'] = data.get('givenName', '')
        payload['last_name'] = data.get('familyName', '')
        payload['email'] = data['email']
        payload['exp'] = time.time() + expiration_mins * 60

        return encode(payload, self.config['AHA_JWT_SECRET'])

    def _execute_asset_approval(self, request):
        print(request)
        request_id = request['id']
        request_type = request['type']
        template_id = self.config['APPROVED_TEMPLATE_ID']
        customer_id = request['asset']['tiers']['customer']['external_id']
        asset_id = request['asset']['id']

        self.logger.info(
            f'Provisioning asset {asset_id} of type {request_type} with id {request_id}',
        )

        try:
            self.client.requests[request_id]('approve').post({'template_id': template_id})
            self.logger.info(
                f"""Successfully provisioned asset {asset_id} for reseller with id {customer_id},
                    request {request_id}""",
            )
            return ProcessingResponse.done()
        except ClientError as exception:
            self.logger.error(
                f'Request type {request_type} {request_id} raised exception {exception}',
            )
            if exception.status_code and exception.status_code >= 500:
                return ProcessingResponse.reschedule()
            raise exception

    def process_asset_purchase_request(self, request):
        return self._execute_asset_approval(request)

    def process_asset_cancel_request(self, request):
        return self._execute_asset_approval(request)

    def process_asset_change_request(self, request):
        return self._execute_asset_approval(request)

    def process_asset_resume_request(self, request):
        return self._execute_asset_approval(request)

    def process_asset_suspend_request(self, request):
        return self._execute_asset_approval(request)

    def execute_product_action(self, request):
        jwt_payload = request['jwt_payload']
        asset_id = jwt_payload['asset_id']

        if request['method'] == 'POST':
            data = request.get('form_data', {})
            email = data.get('email')
            if not email:
                self.logger.error(f'SSO requested for asset {asset_id} with no email')
                location = self.config.get('DEFAULT_REDIRECT', self.DEFAULT_REDIRECT)
                self.logger.info(
                    f'Redirecting SSO request for asset {asset_id} to default site',
                )
            else:
                self.logger.info(f'SSO requested for asset {asset_id} by {email}')
                aha_token = self._calculate_aha_token(data, jwt_payload)
                aha_login_url = self.config['AHA_LOGIN_URL']
                location = f'{aha_login_url}?jwt={aha_token}'
                self.logger.info(
                    f'Redirecting SSO request for asset {asset_id} to login',
                )
        else:
            self.logger.error(f'SSO requested for asset {asset_id} was invoked with invalid method')
            location = self.config.get('DEFAULT_REDIRECT', self.DEFAULT_REDIRECT)
            self.logger.info(
                f'Redirecting SSO request for asset {asset_id} to default site',
            )

        return ProductActionResponse.done(http_status=302, headers={'Location': location})
