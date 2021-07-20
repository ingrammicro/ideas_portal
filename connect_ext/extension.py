# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#
import time
from jwt import encode, decode

from connect.eaas.extension import (
    Extension,
    ProcessingResponse,
    ProductActionResponse
)


class IdeasPortalExtension(Extension):
    
    def _calculate_aha_token(self, request):     
        data = request['form_data']
        connect_token = request['querystring']['jwt'][0]
        jwt_decoded = decode(connect_token, self.config['CONNECT_JWT_SECRET'],  algorithms='HS256')

        payload = {}
        payload['iat'] = int(time.time())
        payload['jti'] = jwt_decoded['asset_id']
        payload['first_name'] = data['givenName']
        payload['last_name'] = data['familyName']
        payload['email'] = data['email']
        payload['exp'] = time.time() + int(self.config.get("TOKEN_EXP_MINUTES", 1)) * 60

        return encode(payload, self.config['AHA_JWT_SECRET'])

    def process_asset_purchase_request(self, request):
        request_id = request['id']
        self.logger.info(f"Obtained request with id {request_id}")
        
        template_id = self.config['APPROVED_TEMPLATE_ID']

        try:
            self.client.requests[request_id]('approve').post({'template_id': template_id})
            self.logger.info(f"Request {request_id} has been processed")
            return ProcessingResponse.done()
        except Exception as ex:
            self.logger.err(f"Request {request_id} raised exception {ex}")
            raise ex
    
    def execute_product_action(self, request):
        self.logger.info(f'Product action: {request}')

        if request['method'] == 'GET':
            return ProductActionResponse.done(
                http_status=302,
                headers={'Location': self.config['DEFAULT_REDIRECT']}
            )

        aha_token = self._calculate_aha_token(request)
        aha_login_url = self.config['AHA_LOGIN_URL']
        return ProductActionResponse.done(
            http_status=302,
            headers={'Location': f"{aha_login_url}?jwt={aha_token}"}
        )
