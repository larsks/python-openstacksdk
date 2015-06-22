# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import os
import tempfile

from os_client_config import cloud_config

import extras
import fixtures
from oslotest import base
import yaml


VENDOR_CONF = {
    'public-clouds': {
        '_test_cloud_in_our_cloud': {
            'auth': {
                'username': 'testotheruser',
                'project_name': 'testproject',
            },
        },
    }
}
USER_CONF = {
    'clouds': {
        '_test-cloud_': {
            'profile': '_test_cloud_in_our_cloud',
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
            },
            'region_name': 'test-region',
        },
        '_test_cloud_no_vendor': {
            'profile': '_test_non_existant_cloud',
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
                'project_name': 'testproject',
            },
            'region-name': 'test-region',
        },
        '_test-cloud-int-project_': {
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
                'project_id': 12345,
            },
            'region_name': 'test-region',
        },
        '_test_cloud_hyphenated': {
            'auth': {
                'username': 'testuser',
                'password': 'testpass',
                'project-id': '12345',
            },
            'region_name': 'test-region',
        }
    },
    'cache': {'max_age': 1},
}
NO_CONF = {
    'cache': {'max_age': 1},
}


def _write_yaml(obj):
    # Assume NestedTempfile so we don't have to cleanup
    with tempfile.NamedTemporaryFile(delete=False) as obj_yaml:
        obj_yaml.write(yaml.safe_dump(obj).encode('utf-8'))
        return obj_yaml.name


class TestCase(base.BaseTestCase):
    """Test case base class for all unit tests."""

    def setUp(self):
        super(TestCase, self).setUp()

        self.useFixture(fixtures.NestedTempfile())
        conf = dict(USER_CONF)
        tdir = self.useFixture(fixtures.TempDir())
        conf['cache']['path'] = tdir.path
        self.cloud_yaml = _write_yaml(conf)
        self.vendor_yaml = _write_yaml(VENDOR_CONF)
        self.no_yaml = _write_yaml(NO_CONF)

        # Isolate the test runs from the environment
        # Do this as two loops because you can't modify the dict in a loop
        # over the dict in 3.4
        keys_to_isolate = []
        for env in os.environ.keys():
            if env.startswith('OS_'):
                keys_to_isolate.append(env)
        for env in keys_to_isolate:
            self.useFixture(fixtures.EnvironmentVariable(env))

    def _assert_cloud_details(self, cc):
        self.assertIsInstance(cc, cloud_config.CloudConfig)
        self.assertTrue(extras.safe_hasattr(cc, 'auth'))
        self.assertIsInstance(cc.auth, dict)
        self.assertIsNone(cc.cloud)
        self.assertIn('username', cc.auth)
        self.assertEqual('testuser', cc.auth['username'])
        self.assertEqual('testproject', cc.auth['project_name'])
