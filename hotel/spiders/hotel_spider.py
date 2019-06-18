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
from collections import namedtuple

import scrapy

from hotel.spiders.data import city, city_data

City = namedtuple('City', ['name', 'url', 'id'])
Hotel = namedtuple('Hotel', ['name', 'url'])


class HotelSpider(scrapy.Spider):
    name = "hotel"
    __host = "https://hotels.ctrip.com"
    _k1 = "全季酒店"

    def start_requests(self):
        for cn in city:
            x = next(x for x in city_data if x['name'] == cn)
            c = City(
                name=c,
                url=HotelSpider.__host + '/hotel/' + x['py'] + x['n'] + '/k1' + HotelSpider._k1 ,
                id=x['n'],
            )
            yield scrapy.FormRequest(
                    url='https://hotels.ctrip.com/Domestic/Tool/AjaxHotelList.aspx',
                    meta={'city': c, 'page': 1, 'todo': -1},
                    callback=self.parse_hotel_api,
                    formdata={
                        '__VIEWSTATEGENERATOR': 'DB1FBB6D',
                        'cityName': c.name,
                        'txtkeyword': HotelSpider._k1,
                        'cityId': c.id,
                        'keyword': HotelSpider._k1,
                        'priceRange': '-2',
                        'OrderBy': '99',
                        'k1': HotelSpider._k1,
                        'page': '1',
                        },
                    )

    def parse_hotel_api(self, response):
        meta = response.meta
        c = meta['city']
        page = meta['page']
        data = json.loads(response.text)
        todo = int(data['hotelAmount']) if page == 1 else meta['todo']
        for h in data['hotelPositionJSON']:
            yield scrapy.Request(
                    url=HotelSpider.__host + h['url'],
                    meta=meta,
                    callback=self.parse,
                    )
            todo -= 1

        if todo > 0:
            yield scrapy.FormRequest(
                    url='https://hotels.ctrip.com/Domestic/Tool/AjaxHotelList.aspx',
                    meta={'city': c, 'page': page, 'todo': todo},
                    callback=self.parse_hotel_api,
                    formdata={
                        '__VIEWSTATEGENERATOR': 'DB1FBB6D',
                        'cityName': c.name,
                        'txtkeyword': HotelSpider._k1,
                        'cityId': c.id,
                        'keyword': HotelSpider._k1,
                        'priceRange': '-2',
                        'OrderBy': '99',
                        'k1': HotelSpider._k1,
                        'page': str(meta['page'] + 1),
                        },
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
            'url': response.request.url,
        }

    def debug(self):
        __import__('IPython').embed()
