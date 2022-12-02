# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Ingram Micro Cloud
# All rights reserved.
#

import re
import time

from connect_ext.extension import IdeasPortalExtension

import pytest

from jwt import decode

from freezegun import freeze_time

TEST_FREEZE_TIME_EPOCH = 1626873720
TEST_FREEZE_TIME = '2021-07-21 13:22:00'


@pytest.mark.parametrize(
    ('request_method', 'redirect_url_key', 'query_string_pattern'),
    (
        ('POST', 'AHA_LOGIN_URL', '\\?jwt=*'),
        ('GET', 'DEFAULT_REDIRECT', ''),
    ),
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
    ('expiration_time_conf', 'expected_expiration'),
    (
        (5, TEST_FREEZE_TIME_EPOCH + 5 * 60),
    ),
)
@freeze_time(TEST_FREEZE_TIME)
def test_process_product_action_aha_payload(
    logger,
    product_action_request_factory,
    product_action_config_factory,
    expiration_time_conf,
    expected_expiration,
):
    config = product_action_config_factory(expiration_time_conf)
    request = product_action_request_factory('POST')

    ext = IdeasPortalExtension(None, logger, config)
    result = ext.execute_product_action(request)
    redirect_url = config['AHA_LOGIN_URL']
    location = result.headers['Location']

    assert result.status == 'success'
    assert result.http_status == 302

    url_pattern = re.compile(f'{redirect_url}\\?jwt=(.*)')
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
    assert expected_expiration == int(jwt_paylod_result['exp'])


@pytest.mark.parametrize(
    ('form_data', 'redirect_url_key', 'query_string_pattern'),
    (
        (
            {'email': '',
             'givenName': 'John',
             'familyName': 'Doe',
             },
            'DEFAULT_REDIRECT',
            '',
        ),
        (
            {'email': 'john.doe@cloudblue.com',
             'givenName': '',
             'familyName': '',
             },
            'AHA_LOGIN_URL',
            '\\?jwt=*',
        ),
    ),
)
def test_process_product_action_aha_form_data(
    logger,
    product_action_request_factory,
    product_action_config_factory,
    form_data,
    redirect_url_key,
    query_string_pattern,
):
    config = product_action_config_factory()

    request = product_action_request_factory(method='POST', form_data=form_data)

    ext = IdeasPortalExtension(None, logger, config)
    result = ext.execute_product_action(request)
    redirect_url = config[redirect_url_key]

    assert result.status == 'success'
    assert result.http_status == 302
    assert re.match(re.compile(f'{redirect_url}{query_string_pattern}'), result.headers['Location'])
