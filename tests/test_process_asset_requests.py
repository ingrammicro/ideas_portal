# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Ingram Micro Cloud
# All rights reserved.
#

import pytest

from connect.client.exceptions import ClientError
from connect.eaas.dataclasses import ResultType


def _execute_asset_process_test(
    request_type,
    extension_for_asset_approval_factory,
    http_status=200,
    exception=None,
):
    request = {
        'id': 1,
        'status': 'pending',
        'type': request_type,
        'asset': {'id': 'AS-1234-1234-1234', 'tiers': {'customer': {'external_id': '9999999'}}},
    }
    ext = extension_for_asset_approval_factory(http_status, exception)
    return getattr(ext, f'process_asset_{request_type}_request')(request)


@pytest.mark.parametrize(
    ('mock_http_status', 'result_status'),
    (
        (200, ResultType.SUCCESS),
        (500, ResultType.RESCHEDULE),
        (501, ResultType.RESCHEDULE),
    ),
)
def test_process_asset_purchase_request(
    extension_for_asset_approval_factory,
    mock_http_status,
    result_status,
):
    result = _execute_asset_process_test(
        'purchase',
        extension_for_asset_approval_factory,
        http_status=mock_http_status,
    )
    assert result.status == result_status


@pytest.mark.parametrize(
    ('mock_http_status', 'result_status'),
    (
        (200, ResultType.SUCCESS),
        (500, ResultType.RESCHEDULE),
        (501, ResultType.RESCHEDULE),
    ),
)
def test_process_asset_cancel_request(
    extension_for_asset_approval_factory,
    mock_http_status,
    result_status,
):
    result = _execute_asset_process_test(
        'cancel',
        extension_for_asset_approval_factory,
        http_status=mock_http_status,
    )
    assert result.status == result_status


@pytest.mark.parametrize(
    ('mock_http_status', 'result_status'),
    (
        (200, ResultType.SUCCESS),
        (500, ResultType.RESCHEDULE),
        (501, ResultType.RESCHEDULE),
    ),
)
def test_process_asset_change_request(
    extension_for_asset_approval_factory,
    mock_http_status,
    result_status,
):
    result = _execute_asset_process_test(
        'change',
        extension_for_asset_approval_factory,
        http_status=mock_http_status,
    )
    assert result.status == result_status


@pytest.mark.parametrize(
    ('mock_http_status', 'result_status'),
    (
        (200, ResultType.SUCCESS),
        (500, ResultType.RESCHEDULE),
        (501, ResultType.RESCHEDULE),
    ),
)
def test_process_asset_resume_request(
    extension_for_asset_approval_factory,
    mock_http_status,
    result_status,
):
    result = _execute_asset_process_test(
        'resume',
        extension_for_asset_approval_factory,
        http_status=mock_http_status,
    )
    assert result.status == result_status


@pytest.mark.parametrize(
    ('mock_http_status', 'result_status'),
    (
        (200, ResultType.SUCCESS),
        (500, ResultType.RESCHEDULE),
        (501, ResultType.RESCHEDULE),
    ),
)
def test_process_asset_suspend_request(
    extension_for_asset_approval_factory,
    mock_http_status,
    result_status,
):
    result = _execute_asset_process_test(
        'suspend',
        extension_for_asset_approval_factory,
        http_status=mock_http_status,
    )
    assert result.status == result_status


def test_process_asset_purchase_request_raise_error(extension_for_asset_approval_factory):
    with pytest.raises(ClientError) as excinfo:
        _execute_asset_process_test('purchase', extension_for_asset_approval_factory, 400)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_cancel_request_raise_error(extension_for_asset_approval_factory):
    with pytest.raises(ClientError) as excinfo:
        _execute_asset_process_test('cancel', extension_for_asset_approval_factory, 400)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_change_request_raise_error(extension_for_asset_approval_factory):
    with pytest.raises(ClientError) as excinfo:
        _execute_asset_process_test('change', extension_for_asset_approval_factory, 400)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_resume_request_raise_error(extension_for_asset_approval_factory):
    with pytest.raises(ClientError) as excinfo:
        _execute_asset_process_test('resume', extension_for_asset_approval_factory, 400)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_suspend_request_raise_error(extension_for_asset_approval_factory):
    with pytest.raises(ClientError) as excinfo:
        _execute_asset_process_test('suspend', extension_for_asset_approval_factory, 400)
        assert '400 Bad Request' in excinfo.value
