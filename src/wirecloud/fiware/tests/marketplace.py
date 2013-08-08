# -*- coding: utf-8 -*-

# Copyright (c) 2013 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of Wirecloud.

# Wirecloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Wirecloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Wirecloud.  If not, see <http://www.gnu.org/licenses/>.

import json
import os
import requests

from wirecloud.commons.utils.testcases import WirecloudTestCase
from wirecloud.fiware.marketAdaptor.marketadaptor import MarketAdaptor
from wirecloud.fiware.tests.store import DynamicWebServer, FakeNetwork, LocalFileSystemServer


class MarketplaceTestCase(WirecloudTestCase):

    tags = ('fiware-ut-8', 'current')

    @classmethod
    def setUpClass(cls):

        super(MarketplaceTestCase, cls).setUpClass()

        cls.network = FakeNetwork({
            'http': {
                'marketplace.example.com': DynamicWebServer(),
                'repository.example.com': LocalFileSystemServer(os.path.join(os.path.dirname(__file__), 'test-data', 'responses', 'repository')),
            },
        })
        cls.network.mock_requests()

    @classmethod
    def tearDownClass(cls):

        super(MarketplaceTestCase, cls).tearDownClass()

        cls.network.unmock_requests()

    def setUp(self):

        super(MarketplaceTestCase, self).setUp()

        self.market_adaptor = MarketAdaptor('http://marketplace.example.com')
        self.network._servers['http']['marketplace.example.com'].clear()
        self.network._servers['http']['marketplace.example.com'].add_response('POST', '/FiwareMarketplace/j_spring_security_check', {'url': 'http://marketplace.example.com/v1/FiwareMarketplace;jsessionid=1111', 'content': ''})

    def read_response_file(self, *response):
        f = open(os.path.join(os.path.dirname(__file__), 'test-data', *response))
        contents = f.read()
        f.close()

        return contents

    def test_marketplace_keyword_search(self):

        response_text = self.read_response_file('responses', 'marketplace', 'keyword_search.xml')
        self.network._servers['http']['marketplace.example.com'].add_response('GET', '/FiwareMarketplace/v1/search/offerings/fulltext/test', {'content': response_text})
        result = self.market_adaptor.full_text_search('', 'test', {})
        expected_result = json.loads(self.read_response_file('results', 'test_marketplace_keyword_search.json'))

        self.assertEqual(result, expected_result)
