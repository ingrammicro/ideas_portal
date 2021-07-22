# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#

import re
import time

import connect

from connect_ext.extension import IdeasPortalExtension

import pytest

from jwt import decode

from freezegun import freeze_time

TEST_FREEZE_TIME_EPOCH = 1626873720
TEST_FREEZE_TIME = '2021-07-21 13:22:00'


def test_process_asset_purchase_request_raise_error(
    sync_client_factory,
    response_factory,
    logger,
):
    config = {'APPROVED_TEMPLATE_ID': 'DUMMY-TEMPLATE-ID'}
    request = {'id': 1, 'status': 'pending', 'type': 'purchase'}
    responses = [
        response_factory(status=400),
    ]
    client = sync_client_factory(responses)
    ext = IdeasPortalExtension(client, logger, config)

    with pytest.raises(connect.client.exceptions.ClientError) as excinfo:
        ext.process_asset_purchase_request(request)
        assert '400 Bad Request' in excinfo.value


def test_process_asset_purchase_request_raise_500_error(
    sync_client_factory,
    response_factory,
    logger,
):
    config = {}
    request = {'id': 1, 'status': 'pending', 'type': 'purchase'}
    responses = [
        response_factory(status=400),
    ]
    client = sync_client_factory(responses)
    ext = IdeasPortalExtension(client, logger, config)

    with pytest.raises(Exception) as excinfo:
        ext.process_asset_purchase_request(request)
        assert '500 Server Error' in excinfo.value


@pytest.mark.parametrize(
    'request_method,redirect_url_key,query_string_pattern',
    [('POST', 'AHA_LOGIN_URL', '\\?jwt=*'),
     ('GET', 'DEFAULT_REDIRECT', '')],
)
def test_process_product_action(
    logger,
    product_action_request_factory,
    product_action_config_factory,
    request_method,
    redirect_url_key,
    query_string_pattern,
):
    config = product_action_config_factory()

    request = product_action_request_factory(request_method)
    ext = IdeasPortalExtension(None, logger, config)
    result = ext.execute_product_action(request)
    redirect_url = config[redirect_url_key]

    assert result.status == 'success'
    assert result.http_status == 302
    assert re.match(re.compile(f'{redirect_url}{query_string_pattern}'), result.headers['Location'])


@pytest.mark.parametrize(
    'expiration_time_conf,expected_expiration',
    [(5, TEST_FREEZE_TIME_EPOCH + 5 * 60),
     (0, TEST_FREEZE_TIME_EPOCH),
     ]
)
@freeze_time(TEST_FREEZE_TIME)
def test_process_product_action_aha_payload(
    logger,
    product_action_request_factory,
    product_action_config_factory,
    expiration_time_conf,
    expected_expiration,
):
    config = product_action_config_factory()
    config['TOKEN_EXP_MINUTES'] = expiration_time_conf

    request = product_action_request_factory('POST')

    ext = IdeasPortalExtension(None, logger, config)
    result = ext.execute_product_action(request)
    redirect_url = config['AHA_LOGIN_URL']
    location = result.headers['Location']

    assert result.status == 'success'
    assert result.http_status == 302

    url_pattern = re.compile(f'{redirect_url}\?jwt=(.+)')
    assert re.match(url_pattern, location)

    freeze_moment = time.time()
    jwt_token = url_pattern.search(location).group(1)
    jwt_paylod_result = decode(jwt_token, config['AHA_JWT_SECRET'], algorithms='HS256')
    request_form_data = request['form_data']
    assert freeze_moment == jwt_paylod_result['iat']
    assert request['jwt_payload']['asset_id'] == jwt_paylod_result['jti']
    assert request_form_data['givenName'] == jwt_paylod_result['first_name']
    assert request_form_data['familyName'] == jwt_paylod_result['last_name']
    assert request_form_data['email'] == jwt_paylod_result['email']
    assert expected_expiration == jwt_paylod_result['exp']
