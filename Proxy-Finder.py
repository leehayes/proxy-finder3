import asyncio
import json
import random
from pprint import pprint

import aiohttp
from bs4 import BeautifulSoup

'''Finds elite anonymity (L1) HTTP proxies asyncronously.
'''

# TO DO:
# -Add lots of sources

__author__ = 'Lee Hayes'
__contact__ = '@leehayes81'


class ProxyFinder(object):
    '''
    The primary class responsible for sourcing, storing and presenting proxy ips
    '''

    def __init__(self, gimme=1, freeproxylistuk=1, freeproxylistus=1):
        self.gimme = gimme
        self.freeproxylist_uk = freeproxylistuk
        self.freeproxylist_us = freeproxylistus
        self.user_agent = [
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        ]
        self.lock = asyncio.Lock()
        self.freeproxylist_uk_list = None
        self.freeproxylist_us_list = None
        self.task_list_of_proxy_sourcing_functions = []
        self.list_of_proxies = self.proxy_details


    async def get_page_json(self, url):
        async with aiohttp.ClientSession() as session:
            user_agent = {"User:Agent": random.choice(self.user_agent)}
            response = await session.request('GET', url, headers=user_agent)
            body = await response.read()
            body = body.decode("utf-8")
            json_res = json.loads(body)
            return json_res

    async def get_page_html(self, url):
        async with aiohttp.ClientSession() as session:
            user_agent = {"User:Agent": random.choice(self.user_agent)}
            response = await session.request('GET', url, headers=user_agent)
            body = await response.read()
            html_res = body.decode("utf-8")
            return html_res

    ########################

    async def view_gimmeproxy(self):
        proxy_json = await self.get_page_json('http://gimmeproxy.com/api/getProxy'
                                              '?get=true&post=true&supportsHttps=true&maxCheckPeriod=3600')
        return proxy_json

    async def create_proxy_dict_gimmeproxy(self):
        proxy_json = await self.view_gimmeproxy()
        if proxy_json.get('status_code') == 429:
            return 'Limit Exceeded'
        proxy_dict = {'ip': proxy_json.get('ip'),
                      'port': proxy_json.get('port'),
                      'source': 'http://gimmeproxy.com/api/getProxy'}
        return proxy_dict

    ########################

    async def view_freeproxylist_uk(self):
        html = await self.get_page_html('https://free-proxy-list.net/uk-proxy.html')
        return html

    async def create_proxy_dict_freeproxylist_uk(self, index):
        await self.lock.acquire()
        if self.freeproxylist_uk_list == None:
            html = await self.view_freeproxylist_uk()
            soup = BeautifulSoup(html, "lxml")

            self.freeproxylist_uk_list = []
            for table in soup.findAll('table', {'class': 'table'}):
                for row in table.findAll('tr'):
                    row_list = [cell.text for cell in row.findAll('td')]
                    if row_list:
                        proxy_dict = {}
                        proxy_dict['source'] = 'https://free-proxy-list.net/uk-proxy.html'
                        proxy_dict['ip'] = row_list[0]
                        proxy_dict['port'] = row_list[1]
                        self.freeproxylist_uk_list.append(proxy_dict)
            self.lock.release()
        else:
            self.lock.release()

        if index >= len(self.freeproxylist_uk_list):
            return None
        return self.freeproxylist_uk_list[index]

    ########################

    async def view_freeproxylist_us(self):
        html = await self.get_page_html('https://free-proxy-list.net/us-proxy.html')
        return html

    async def create_proxy_dict_freeproxylist_us(self, index):
        await self.lock.acquire()
        if self.freeproxylist_us_list == None:
            html = await self.view_freeproxylist_us()
            soup = BeautifulSoup(html, "lxml")
            self.freeproxylist_us_list = []
            for table in soup.findAll('table', {'id': 'proxylisttable'}):
                for row in table.findAll('tr'):
                    row_list = [cell.text for cell in row.findAll('td')]
                    if row_list:
                        proxy_dict = {}
                        proxy_dict['source'] = 'https://free-proxy-list.net/us-proxy.html'
                        proxy_dict['ip'] = row_list[0]
                        proxy_dict['port'] = row_list[1]
                        self.freeproxylist_us_list.append(proxy_dict)
            self.lock.release()
        else:
            self.lock.release()

        if index >= len(self.freeproxylist_us_list):
            return None
        return self.freeproxylist_us_list[index]

    ########################

    @property
    def proxy_details(self):
        '''
        Return proxy ips for .....
        :return: a list of dictionaries detailing proxy details
        '''

        if not self.gimme + self.freeproxylist_uk + self.freeproxylist_us:
            return "No sources selected"

        # Add Gimme tasks to task list
        for i in range(self.gimme):
            task = asyncio.ensure_future(self.create_proxy_dict_gimmeproxy())
            self.task_list_of_proxy_sourcing_functions.append(task)

        # Add FreeProxyListuk tasks to task list
        for i in range(self.freeproxylist_uk):
            task = asyncio.ensure_future(self.create_proxy_dict_freeproxylist_uk(i))
            self.task_list_of_proxy_sourcing_functions.append(task)

        # Add FreeProxyListus tasks to task list
        for i in range(self.freeproxylist_us):
            task = asyncio.ensure_future(self.create_proxy_dict_freeproxylist_us(i))
            self.task_list_of_proxy_sourcing_functions.append(task)


        loop = asyncio.get_event_loop()
        done, _ = loop.run_until_complete(asyncio.wait(self.task_list_of_proxy_sourcing_functions))
        results = []
        for fut in done:
            results.append(fut.result())
        loop.close()
        # results = list(itertools.chain(*results))
        return results



if __name__ == "__main__":
    pf = ProxyFinder(gimme=0, freeproxylistuk=2, freeproxylistus=2)
    pprint(pf.list_of_proxies)

    # TODO: http://www.gatherproxy.com/
