# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#

from connect.eaas.extension import (
    Extension,
    ProcessingResponse,
    ProductActionResponse
)


class IdeasPortalExtension(Extension):
    
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
        return ProductActionResponse.done()