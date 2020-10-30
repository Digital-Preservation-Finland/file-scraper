# -*- coding: utf-8 -*-
"""Comments"""
from pprint import pprint
from file_scraper.detectors import FidoDetector
from file_scraper.scraper import Scraper

image_1 = 'zfoo/0003.tif'
image_2 = 'zfoo/0005.tif'

aaa = Scraper(image_1)
aaa.scrape(check_wellformed=True)

pprint(aaa.__dict__)
