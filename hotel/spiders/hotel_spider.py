#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 jack <jack@6k>
#
# Distributed under terms of the MIT license.

"""
crawl hotels from ctrip.com
"""

import json
import logging
from collections import namedtuple

import scrapy
import lxml

from config.data import *

City = namedtuple('City', ['name', 'url', 'id'])
Hotel = namedtuple('Hotel', ['name', 'url'])


class HotelSpider(scrapy.Spider):
    name = "hotel"
    __host = "https://hotels.ctrip.com"

    def __make_api_call(self, city, page, todo, k1):
        return scrapy.FormRequest(
            url='https://hotels.ctrip.com/Domestic/Tool/AjaxHotelList.aspx',
            meta={'city': city, 'page': page, 'todo': todo, 'k1': k1},
            callback=self.parse_hotel_api,
            formdata={
                '__VIEWSTATEGENERATOR': 'DB1FBB6D',
                'cityName': city.name,
                'txtkeyword': k1,
                'cityId': city.id,
                'keyword': k1,
                'priceRange': '-2',
                'OrderBy': '99',
                'k1': k1,
                'page': '1',
            },
        )

    def start_requests(self):
        k1 = getattr(self, 'k1', '全季酒店')
        for cn in TARGET_CITIES:
            x = next((x for x in DATA_CITY_ID if x['name'] == cn), None)
            if not x:
                self.log('CityID not found: %s' % cn, logging.ERROR)
                continue
            yield self.__make_api_call(
                city=City(
                    name=cn,
                    url=HotelSpider.__host + '/hotel/' + x['py'] + x['n'] + '/k1' + k1,
                    id=x['n'],
                ),
                page=1,
                todo=-1,
                k1=k1,
            )

    def parse_hotel_api(self, response):
        meta = response.meta
        data = json.loads(response.text)

        # if there is no hotel in city, api will return warning in <h2>
        tmp = lxml.html.fromstring('<tmp>' + data['hotelList'] + '</tmp>')
        if tmp.xpath('./h2'):
            self.log('No hotels found: %s @ %s' % (meta['k1'], meta['city'].name), logging.WARNING)
            return

        page = meta['page']
        todo = int(data['hotelAmount']) if page == 1 else meta['todo']
        for h in data['hotelPositionJSON']:
            yield scrapy.Request(
                    url=HotelSpider.__host + h['url'],
                    meta=meta,
                    callback=self.parse,
                    )
            todo -= 1

        if todo > 0:
            yield self.__make_api_call(
                city=meta['city'],
                page=meta['page'],
                todo=todo,
                k1=meta['k1'],
            )

    def parse(self, response):
        # split by '&nbsp;&nbsp;'
        # format: <start_year><s>(<?><s>)<size><s>
        desc = response.xpath('//div[@id="htlDes"]/p/text()').get().strip().split('\xc2\xa0\xc2\xa0'.decode('utf8'))
        yield {
            'city': response.meta['city'].name,
            'name': response.xpath('//h2[@class="cn_n"]/text()').get(),
            'en': response.xpath('//h2[@class="en_n"]/text()').get(),
            'start_year': desc[0],
            'size': desc[-1],
            'url': response.request.url.split('?')[0],
        }

    def debug(self):
        __import__('IPython').embed()
