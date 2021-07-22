# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#

import connect

from connect_ext.extension import IdeasPortalExtension

import pytest


def _execute_asset_process_test(request_type, extension_for_asset_aproval_factory, http_status=200):
    request = {'id': 1, 'status': 'pending', 'type': request_type}
    ext = extension_for_asset_aproval_factory(http_status)
    return getattr(ext, f'process_asset_{request_type}_request')(request)


def test_process_asset_purchase_request(extension_for_asset_aproval_factory):
    result = _execute_asset_process_test('purchase', extension_for_asset_aproval_factory)
    assert result.status == 'success'


def test_process_asset_cancel_request(extension_for_asset_aproval_factory):
    result = _execute_asset_process_test('cancel', extension_for_asset_aproval_factory)
    assert result.status == 'success'


def test_process_asset_change_request(extension_for_asset_aproval_factory):
    result = _execute_asset_process_test('change', extension_for_asset_aproval_factory)
    assert result.status == 'success'


def test_process_asset_resume_request(extension_for_asset_aproval_factory):
    result = _execute_asset_process_test('resume', extension_for_asset_aproval_factory)
    assert result.status == 'success'


def test_process_asset_suspend_request(extension_for_asset_aproval_factory):
    result = _execute_asset_process_test('suspend', extension_for_asset_aproval_factory)
    assert result.status == 'success'


def test_process_asset_purchase_request_raise_error(extension_for_asset_aproval_factory):
    with pytest.raises(connect.client.exceptions.ClientError) as excinfo:
        _execute_asset_process_test('purchase', extension_for_asset_aproval_factory, 400)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_cancel_request_raise_error(extension_for_asset_aproval_factory):
    with pytest.raises(connect.client.exceptions.ClientError) as excinfo:
        _execute_asset_process_test('cancel', extension_for_asset_aproval_factory, 400)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_change_request_raise_error(extension_for_asset_aproval_factory):
    with pytest.raises(connect.client.exceptions.ClientError) as excinfo:
        _execute_asset_process_test('change', extension_for_asset_aproval_factory, 400)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_resume_request_raise_error(extension_for_asset_aproval_factory):
    with pytest.raises(connect.client.exceptions.ClientError) as excinfo:
        _execute_asset_process_test('resume', extension_for_asset_aproval_factory, 400)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_suspend_request_raise_error(extension_for_asset_aproval_factory):
    with pytest.raises(connect.client.exceptions.ClientError) as excinfo:
        _execute_asset_process_test('suspend', extension_for_asset_aproval_factory, 400)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_purchase_request_raise_500_error(
    sync_client_factory,
    response_factory,
    logger,
):
    config = {}
    request = {'id': 1, 'status': 'pending'}
    responses = [
        response_factory(status=400),
    ]
    client = sync_client_factory(responses)
    ext = IdeasPortalExtension(client, logger, config)

    with pytest.raises(Exception) as excinfo:
        ext.process_asset_purchase_request(request)
        assert '500 Server Error' in excinfo.value
