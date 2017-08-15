#!/usr/bin/env python3.5

'''Finds elite anonymity (L1) HTTP proxies asyncronously.
'''

# TO DO:
# -Add lots of sources

__author__ = 'Lee Hayes'
__contact__ = '@leehayes81'


import sys, re, time, os, argparse
from BeautifulSoup4 import BeautifulSoup
