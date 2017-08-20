import asyncio
from unittest import TestCase

import requests
from hamcrest import *
from proxy.ProxyFinder import ProxyFinder


class TestProxyFinder(TestCase):
    def setUp(self):
        self.pf = ProxyFinder()
        self.loop = asyncio.get_event_loop()

    def test_repr(self):
        self.pf2 = ProxyFinder(gimme=1, freeproxylistuk=1, freeproxylistus=2, gatherproxy=2)
        assert_that(repr(self.pf),
                    equal_to("ProxyFinder(gimme=1, freeproxylistuk=1, freeproxylistus=1, gatherproxy=1)"))
        assert_that(repr(self.pf2),
                    equal_to("ProxyFinder(gimme=1, freeproxylistuk=1, freeproxylistus=2, gatherproxy=2)"))

    def test_get_page_json(self):
        task_list = [asyncio.ensure_future(self.pf.get_page_json('https://jsonplaceholder.typicode.com/posts'))]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        assert_that(results[0], instance_of(list))
        assert_that(results[0][0], instance_of(dict))

    def test_get_page_html(self):
        task_list = [asyncio.ensure_future(self.pf.get_page_html('http://www.gatherproxy.com/'))]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        assert_that(results[0], instance_of(str))

    def test_view_gimmeproxy(self):
        task_list = [asyncio.ensure_future(self.pf.view_gimmeproxy())]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        view_gimmeproxy_result = results[0]
        requests_result = requests.get(
            'http://gimmeproxy.com/api/getProxy?get=true&post=true&supportsHttps=true&maxCheckPeriod=3600')

        assert_that(view_gimmeproxy_result, equal_to(requests_result.json()))

    def test_create_proxy_dict_gimmeproxy(self):
        task_list = [asyncio.ensure_future(self.pf.create_proxy_dict_gimmeproxy())]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        assert_that(results[0], instance_of(dict))

    def test_view_freeproxylist_uk(self):
        task_list = [asyncio.ensure_future(self.pf.view_freeproxylist_uk())]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        view_freeproxylist_uk_result = results[0]
        requests_result = requests.get('https://free-proxy-list.net/uk-proxy.html')
        assert_that(view_freeproxylist_uk_result, equal_to(requests_result.text))

    def test_create_proxy_dict_freeproxylist_uk(self):
        task_list = [asyncio.ensure_future(self.pf.create_proxy_dict_freeproxylist_uk(1))]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        assert_that(results[0], instance_of(dict))

    def test_view_freeproxylist_us(self):
        task_list = [asyncio.ensure_future(self.pf.view_freeproxylist_us())]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        view_freeproxylist_us_result = results[0]
        requests_result = requests.get('https://free-proxy-list.net/us-proxy.html')
        assert_that(view_freeproxylist_us_result, equal_to(requests_result.text))

    def test_create_proxy_dict_freeproxylist_us(self):
        task_list = [asyncio.ensure_future(self.pf.create_proxy_dict_freeproxylist_us(1))]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        assert_that(results[0], instance_of(dict))

    def test_view_gatherproxy(self):
        task_list = [asyncio.ensure_future(self.pf.view_gatherproxy())]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        view_gatherproxy_result = results[0]
        requests_result = requests.get('http://www.gatherproxy.com/')
        assert_that(view_gatherproxy_result[50], equal_to(requests_result.text[50]))

    def test_create_proxy_dict_gatherproxy(self):
        task_list = [asyncio.ensure_future(self.pf.create_proxy_dict_gatherproxy(1))]
        done, _ = self.loop.run_until_complete(asyncio.wait(task_list))
        results = []
        for fut in done:
            results.append(fut.result())
        assert_that(results[0], instance_of(dict))

    def test_proxy_details(self):
        pf_result = self.pf.proxy_details
        assert_that(pf_result, instance_of(list))
        assert_that(pf_result[0], instance_of(dict))

    def test_refresh(self):
        original_length = len(self.pf.proxy_details)
        refresh_result = self.pf.refresh()
        assert_that(len(refresh_result), equal_to(original_length))
        assert_that(refresh_result, instance_of(list))
        assert_that(refresh_result[0], instance_of(dict))
