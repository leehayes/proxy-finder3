import asyncio
import json
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

    def __init__(self, gimme=1, freeproxylist=1):
        self.gimme = gimme
        self.freeproxylist = freeproxylist
        self.lock = asyncio.Lock()
        self.freeproxylist_soup = None
        self.task_list_of_proxy_sourcing_functions = []
        self.list_of_proxies = self.proxy_details


    async def get_page_json(self, url):
        async with aiohttp.ClientSession() as session:
            response = await session.request('GET', url)
            body = await response.read()
            body = body.decode("utf-8")
            json_res = json.loads(body)
            return json_res

    async def get_page_html(self, url):
        async with aiohttp.ClientSession() as session:
            response = await session.request('GET', url)
            body = await response.read()
            html_res = body.decode("utf-8")
            return html_res

    ########################

    async def view_gimmeproxy(self):
        json = await self.get_page_json('http://gimmeproxy.com/api/getProxy')
        return json

    async def create_proxy_dict_gimmeproxy(self):
        json = await self.view_gimmeproxy()
        dict = {'ip': json.get('ip'), 'port': json.get('port'), 'source': 'http://gimmeproxy.com/api/getProxy'}
        return dict
    ########################

    async def view_freeproxylist(self):
        html = await self.get_page_html('https://free-proxy-list.net/uk-proxy.html')
        return html

    async def create_proxy_dict_freeproxylist(self):
        await self.lock.acquire()
        if self.freeproxylist_soup == None:
            html = await self.view_freeproxylist()
            self.freeproxylist_soup = BeautifulSoup(html, "lxml")
            soup = self.freeproxylist_soup
        else:
            soup = self.freeproxylist_soup
        self.lock.release()

        proxy_list = []

        for table in soup.findAll('table', {'class': 'table'}):
            for row in table.findAll('tr'):
                row_list = [cell.text for cell in row.findAll('td')]
                if row_list:
                    proxy_dict = {'source': 'https://free-proxy-list.net/uk-proxy.html'}
                    proxy_dict['ip'] = row_list[0]
                    proxy_dict['port'] = row_list[1]
                    proxy_list.append(proxy_dict)

        return proxy_list[1]

    ########################

    @property
    def proxy_details(self):
        '''
        Return proxy ips for .....
        :return: a list of dictionaries detailing proxy details
        '''

        # Add Gimme tasks to task list
        for i in range(self.gimme):
            task = asyncio.ensure_future(self.create_proxy_dict_gimmeproxy())
            self.task_list_of_proxy_sourcing_functions.append(task)

        # Add FreeProxyList tasks to task list
        for i in range(self.freeproxylist):
            task = asyncio.ensure_future(self.create_proxy_dict_freeproxylist())
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
    pf = ProxyFinder(gimme=1, freeproxylist=1)
    pprint(pf.list_of_proxies)
