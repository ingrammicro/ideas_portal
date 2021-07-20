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


def test_process_product_action(
    logger,
    product_action_request_factory,
    product_action_config_factory
):
    config = product_action_config_factory()

    aha_login_url = config['AHA_LOGIN_URL']
    request = product_action_request_factory('POST', config['CONNECT_JWT_SECRET'])
    ext = IdeasPortalExtension(None, logger, config)
    
    result = ext.execute_product_action(request)
    assert result.status == 'success'
    assert result.http_status == 302
    assert re.match(re.compile(f'{aha_login_url}\\?jwt=.+'), result.headers['Location'])


def test_process_product_action_get_method(
    logger,
    product_action_config_factory,
    product_action_request_factory
):
    config = product_action_config_factory()
    request = product_action_request_factory('GET', config['CONNECT_JWT_SECRET'])
    ext = IdeasPortalExtension(None, logger, config)
    
    result = ext.execute_product_action(request)
    assert result.status == 'success'
    assert result.http_status == 302
    assert re.match(re.compile(config['DEFAULT_REDIRECT']), result.headers['Location'])
