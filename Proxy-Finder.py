from functools import wraps

'''Finds elite anonymity (L1) HTTP proxies asyncronously.
'''

# TO DO:
# -Add lots of sources

__author__ = 'Lee Hayes'
__contact__ = '@leehayes81'


def proxy_source(method):
    @wraps
    def wrapper(self, *args, **kwargs):
        print("dfasd")
        self.proxy_sourcing_functions.append(method)
        return method(self, *args, **kwargs)

    return wrapper


class ProxyFinder(object):
    '''
    The primary class responsible for sourcing, storing and presenting proxy ips
    '''

    def __init__(self):
        self.proxy_sourcing_functions = []
        pass

    def all_sources(self):
        for func in self.proxy_sourcing_functions:
            print(func)

    @proxy_source
    def get_proxy_from_sitename(self, ):
        '''
        Return proxy ips for .....
        :return: a list of dictionaries detailing proxy details
        '''
        return 45


if __name__ == "__main__":
    pf = ProxyFinder()
    pf.all_sources()
    # pf.get_proxy_from_sitename
