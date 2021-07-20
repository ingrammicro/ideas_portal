# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#

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
