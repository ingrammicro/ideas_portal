# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#

import re
import pytest


import connect
from connect_ext.extension import IdeasPortalExtension


def test_process_asset_purchase_request(
    sync_client_factory,
    response_factory,
    logger
):
    config = {'APPROVED_TEMPLATE_ID': 'DUMMY-TEMPLATE-ID'}
    request = {'id': 1, 'status': 'pending'}
    responses = [
        response_factory(status=200),
    ]
    client = sync_client_factory(responses)
    ext = IdeasPortalExtension(client, logger, config)
    result = ext.process_asset_purchase_request(request)
    assert result.status == 'success'


def test_process_asset_purchase_request_raise_error(
    sync_client_factory,
    response_factory,
    logger,
):
    config = {'APPROVED_TEMPLATE_ID': 'DUMMY-TEMPLATE-ID'}
    request = {'id': 1, 'status': 'pending'}
    responses = [
        response_factory(status=400),
    ]
    client = sync_client_factory(responses)
    ext = IdeasPortalExtension(client, logger, config)

    with pytest.raises(connect.client.exceptions.ClientError) as excinfo:
        ext.process_asset_purchase_request(request)
        assert '400 Bad Request' in excinfo.value


@pytest.mark.parametrize(
    "request_method,redirect_url_key,query_string_pattern", 
    [("POST", "AHA_LOGIN_URL", "\\?jwt=*"), 
    ("GET", "DEFAULT_REDIRECT", "")])
def test_process_product_action(
    logger,
    product_action_request_factory,
    product_action_config_factory,
    request_method,
    redirect_url_key,
    query_string_pattern
):
    config = product_action_config_factory()
    
    request = product_action_request_factory(request_method, config['CONNECT_JWT_SECRET'])
    ext = IdeasPortalExtension(None, logger, config)
    
    result = ext.execute_product_action(request)
    redirect_url = config[redirect_url_key]
    assert result.status == 'success'
    assert result.http_status == 302
    assert re.match(re.compile(f'{redirect_url}{query_string_pattern}'), result.headers['Location'])
