# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#
import time

from connect.eaas.extension import (
    Extension,
    ProcessingResponse,
    ProductActionResponse,
)

from jwt import encode


class IdeasPortalExtension(Extension):

    DEFAULT_REDIRECT = 'https://ingrammicrocloud.com'
    DEFAULT_EXPIRATION_MINUTES = 1

    def _calculate_aha_token(self, request):
        data = request['form_data']
        jwt_payload = request['jwt_payload']
        expiration_mins = self.config.get("TOKEN_EXP_MINUTES")
        expiration_mins = expiration_mins if expiration_mins else self.DEFAULT_EXPIRATION_MINUTES

        payload = {}
        payload['iat'] = int(time.time())
        payload['jti'] = jwt_payload['asset_id']
        payload['first_name'] = data['givenName']
        payload['last_name'] = data['familyName']
        payload['email'] = data['email']
        payload['exp'] = time.time() + expiration_mins * 60

        return encode(payload, self.config['AHA_JWT_SECRET'])

    def process_asset_purchase_request(self, request):
        request_id = request['id']
        self.logger.info(f"Obtained request with id {request_id}")

        template_id = self.config['APPROVED_TEMPLATE_ID']

        try:
            self.client.requests[request_id]('approve').post({'template_id':
                                                              template_id})
            self.logger.info(f"Request {request_id} has been processed")
            return ProcessingResponse.done()
        except Exception as ex:
            self.logger.err(f"Request {request_id} raised exception {ex}")
            raise ex

    def execute_product_action(self, request):
        asset_id = request['jwt_payload']['asset_id']
        action_id = request['jwt_payload']['action_id']
        self.logger.info(f'Starting {action_id} for asset with id {asset_id}')

        if request['method'] == 'POST':
            aha_token = self._calculate_aha_token(request)
            aha_login_url = self.config['AHA_LOGIN_URL']
            location = f"{aha_login_url}?jwt={aha_token}"
        else:
            location = self.config.get('DEFAULT_REDIRECT', self.DEFAULT_REDIRECT)

        self.logger.info(
            f'Action {action_id} for asset {asset_id} redirecting to location {location}',
        )
        return ProductActionResponse.done(http_status=302, headers={'Location': location})
