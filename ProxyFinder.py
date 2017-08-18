import asyncio
import json
import random

import aiohttp
from bs4 import BeautifulSoup

'''Finds elite anonymity (L1) HTTP proxies asyncronously.
'''

# TO DO:
# -Add lots of sources

__author__ = 'Lee Hayes'
__contact__ = '@leehayes81'


class ProxyFinder(object):
    """
    The primary class responsible for sourcing, storing and presenting proxy ips
    """

    def __init__(self, gimme=1, freeproxylistuk=1, freeproxylistus=1, gatherproxy=1):
        """
        ProxyFinder creates an instance that retrieves proxy details from the sources provided.
        If you wish to ignore a particular source, then provide it with the value 0.
        The default is one proxy from each source:
        :param gimme: http://gimmeproxy.com/api/getProxy?get=true&post=true&supportsHttps=true&maxCheckPeriod=3600
        :param freeproxylistuk: https://free-proxy-list.net/uk-proxy.html
        :param freeproxylistus: https://free-proxy-list.net/us-proxy.html
        """
        self.gimme = gimme
        self.freeproxylist_uk = freeproxylistuk
        self.freeproxylist_us = freeproxylistus
        self.gatherproxy = gatherproxy
        self.user_agent = [
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        ]
        self.lock = asyncio.Lock()
        # sites which provide tables or proxies will need to store the table as a list
        self.freeproxylist_uk_list = None
        self.freeproxylist_us_list = None
        self.gatherproxy_list = None
        self.task_list_of_proxy_sourcing_functions = []

    async def get_page_json(self, url):
        """
        Async method to return json from a url
        :param url: Full url, must point to a data source in json format
        :return: Pythonic representation of a json file
        """
        async with aiohttp.ClientSession() as session:
            user_agent = {"User:Agent": random.choice(self.user_agent)}
            response = await session.request('GET', url, headers=user_agent)
            body = await response.read()
            body = body.decode("utf-8")
            json_res = json.loads(body)
            return json_res

    async def get_page_html(self, url):
        """
        Async method to return html from a url
        :param url: Full url, must point to a data source in html format
        :return: html as string
        """
        async with aiohttp.ClientSession() as session:
            user_agent = {"User:Agent": random.choice(self.user_agent)}
            response = await session.request('GET', url, headers=user_agent)
            body = await response.read()
            html_res = body.decode("utf-8")
            return html_res

    ########################

    async def view_gimmeproxy(self):
        """
        Call the url of the website containing proxies. In this case, a single proxy in json format
        :return: Pythonic representation of a json file
        """
        proxy_json = await self.get_page_json('http://gimmeproxy.com/api/getProxy'
                                              '?get=true&post=true&supportsHttps=true&maxCheckPeriod=3600')
        return proxy_json

    async def create_proxy_dict_gimmeproxy(self):
        """
        Create a dictionary of, in this case, a single proxy
        :return: A dictionary containing the proxy ip, port and source url
        """
        proxy_json = await self.view_gimmeproxy()
        if proxy_json.get('status_code') == 429:
            return {'Limit Exceeded': 'gimmeproxy'}
        proxy_dict = {'ip': proxy_json.get('ip'),
                      'port': proxy_json.get('port'),
                      'source': 'http://gimmeproxy.com/api/getProxy'}
        return proxy_dict

    ########################

    async def view_freeproxylist_uk(self):
        """
        Call the url of the website containing a html table of proxy details
        :return: html as a string
        """
        html = await self.get_page_html('https://free-proxy-list.net/uk-proxy.html')
        return html

    async def create_proxy_dict_freeproxylist_uk(self, index):
        """
        When this method runs for the first time it downloads and stores the data taken from the results table.
        All further instances of this method use this stored data which is held until the refresh method is called.
        The final step is to select a row, using index.
        :param index: The row of the table to take.
        :return: A dictionary representing a single proxy address. IP, Port and Source URL
        """
        await self.lock.acquire()
        if self.freeproxylist_uk_list is None:
            html = await self.view_freeproxylist_uk()
            soup = BeautifulSoup(html, "lxml")

            self.freeproxylist_uk_list = []
            for table in soup.findAll('table', {'class': 'table'}):
                for row in table.findAll('tr'):
                    row_list = [cell.text for cell in row.findAll('td')]
                    if row_list:
                        proxy_dict = {'source': 'https://free-proxy-list.net/uk-proxy.html', 'ip': row_list[0],
                                      'port': row_list[1]}
                        self.freeproxylist_uk_list.append(proxy_dict)
            self.lock.release()
        else:
            self.lock.release()

        if index >= len(self.freeproxylist_uk_list):
            return None
        return self.freeproxylist_uk_list[index]

    ########################

    async def view_freeproxylist_us(self):
        """
        Call the url of the website containing a html table of proxy details
        :return: html as a string
        """
        html = await self.get_page_html('https://free-proxy-list.net/us-proxy.html')
        return html

    async def create_proxy_dict_freeproxylist_us(self, index):
        """
        When this method runs for the first time it downloads and stores the data taken from the results table.
        All further instances of this method use this stored data which is held until the refresh method is called.
        The final step is to select a row, using index.
        :param index: The row of the table to take.
        :return: A dictionary representing a single proxy address. IP, Port and Source URL
        """
        await self.lock.acquire()
        if self.freeproxylist_us_list is None:
            html = await self.view_freeproxylist_us()
            soup = BeautifulSoup(html, "lxml")
            self.freeproxylist_us_list = []
            for table in soup.findAll('table', {'id': 'proxylisttable'}):
                for row in table.findAll('tr'):
                    row_list = [cell.text for cell in row.findAll('td')]
                    if row_list:
                        proxy_dict = {'source': 'https://free-proxy-list.net/us-proxy.html', 'ip': row_list[0],
                                      'port': row_list[1]}
                        self.freeproxylist_us_list.append(proxy_dict)
            self.lock.release()
        else:
            self.lock.release()

        if index >= len(self.freeproxylist_us_list):
            return None
        return self.freeproxylist_us_list[index]

    ########################

    async def view_gatherproxy(self):
        """
        Call the url of the website containing a html table of proxy details
        :return: html as a string
        """
        html = await self.get_page_html('http://www.gatherproxy.com/')
        return html

    async def create_proxy_dict_gatherproxy(self, index):
        """
        When this method runs for the first time it downloads and stores the data taken from the results table.
        All further instances of this method use this stored data which is held until the refresh method is called.
        The final step is to select a row, using index.
        :param index: The row of the table to take.
        :return: A dictionary representing a single proxy address. IP, Port and Source URL
        """
        await self.lock.acquire()
        if self.gatherproxy_list is None:
            html = await self.view_gatherproxy()
            soup = BeautifulSoup(html, "lxml")
            self.gatherproxy_list = []

            for table in soup.findAll('table', {'id': 'tblproxy'}):
                for row in table.findAll('script', {'type': 'text/javascript'}):
                    haystack = row.text
                    list_colon_loc = [index for index, needle in enumerate(haystack) if needle == ":"]
                    list_comma_loc = [index for index, needle in enumerate(haystack) if needle == ","]

                    proxy_dict = {'source': 'http://www.gatherproxy.com/',
                                  'ip': haystack[list_colon_loc[2] + 2:list_comma_loc[2] - 1],
                                  'port': str(int(haystack[list_colon_loc[4] + 2:list_comma_loc[4] - 1], 16))}
                    self.gatherproxy_list.append(proxy_dict)

            self.lock.release()
        else:
            self.lock.release()

        if index >= len(self.gatherproxy_list):
            return None
        return self.gatherproxy_list[index]

    ########################

    @property
    def proxy_details(self):
        """
        Extract proxy details from the source urls
        :return: a list of dictionaries detailing proxy details
        """

        if not self.gimme + self.freeproxylist_uk + self.freeproxylist_us + self.gatherproxy:
            return "No sources selected"

        # Add Gimme tasks to task list
        for i in range(self.gimme):
            task = asyncio.ensure_future(self.create_proxy_dict_gimmeproxy())
            self.task_list_of_proxy_sourcing_functions.append(task)

        # Add FreeProxyListUk tasks to task list
        for i in range(self.freeproxylist_uk):
            task = asyncio.ensure_future(self.create_proxy_dict_freeproxylist_uk(i))
            self.task_list_of_proxy_sourcing_functions.append(task)

        # Add FreeProxyListUs tasks to task list
        for i in range(self.freeproxylist_us):
            task = asyncio.ensure_future(self.create_proxy_dict_freeproxylist_us(i))
            self.task_list_of_proxy_sourcing_functions.append(task)

        # Add GatherProxy tasks to task list
        for i in range(self.gatherproxy):
            task = asyncio.ensure_future(self.create_proxy_dict_gatherproxy(i))
            self.task_list_of_proxy_sourcing_functions.append(task)

        loop = asyncio.get_event_loop()
        done, _ = loop.run_until_complete(asyncio.wait(self.task_list_of_proxy_sourcing_functions))

        results = []
        for fut in done:
            results.append(fut.result())

        # loop.close() #keep loop open for refresh method
        # results = list(itertools.chain(*results))
        return results

    def refresh(self):
        self.task_list_of_proxy_sourcing_functions = []
        self.freeproxylist_uk_list = None
        self.freeproxylist_us_list = None
        self.gatherproxy_list = None
        return self.proxy_details


pf = ProxyFinder()
print(len(pf.proxy_details))
